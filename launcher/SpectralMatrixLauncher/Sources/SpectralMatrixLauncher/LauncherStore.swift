import AppKit
import Foundation

@MainActor
final class LauncherStore: ObservableObject {
    @Published private(set) var state: LauncherRunState = .stopped
    @Published private(set) var localHTTPReachable = false
    @Published private(set) var logText = ""
    @Published private(set) var lastCopiedURL: String?

    let localURL = "http://127.0.0.1:8765/"

    private let projectRoot: URL
    private let logFileURL: URL
    private var process: Process?
    private var outputPipe: Pipe?
    private var healthTask: Task<Void, Never>?
    private var shouldStartAfterStop = false
    private var shouldOpenWhenReachable = false
    private var didRequestLaunchStart = false

    init(projectRoot: URL = ProjectRootResolver.resolve()) {
        self.projectRoot = projectRoot
        self.logFileURL = projectRoot.appendingPathComponent("logs/launcher_backend.log")
        prepareLogFile()
        appendLog("光谱训练矩阵启动台已就绪。")
        appendLog("项目根目录：\(projectRoot.path)")
        appendLog("本机工作台：\(localURL)")
        appendLog("日志文件：\(logFileURL.path)")
        startHealthChecks()
    }

    var endpoint: LauncherEndpoint {
        LauncherEndpoint(
            id: "local-workbench",
            title: "本机工作台",
            subtitle: "FastAPI · 8765",
            url: localURL,
            note: "启动后在这台 Mac 上使用；界面能力来自当前光谱平台，不额外加入 REDMath 的公网入口或访问管理。",
            symbolName: "waveform.path.ecg.rectangle"
        )
    }

    var projectRootPath: String {
        projectRoot.path
    }

    var logFilePath: String {
        logFileURL.path
    }

    var canStartServices: Bool {
        !isOwnedProcessActive && state != .starting && state != .restarting && state != .stopping
    }

    var canRestartServices: Bool {
        state != .starting && state != .restarting && state != .stopping
    }

    var canStopServices: Bool {
        isOwnedProcessActive && state != .stopping
    }

    var isOwnedProcessActive: Bool {
        process?.isRunning == true
    }

    func startAndOpen() {
        startServices(openWhenReady: true)
    }

    func startOnLaunch() {
        guard !didRequestLaunchStart else {
            return
        }
        didRequestLaunchStart = true
        appendLog("正在自动检查并启动本机工作台。")
        startServices(openWhenReady: true)
    }

    func startServices(openWhenReady: Bool = false) {
        guard canStartServices else {
            return
        }
        shouldOpenWhenReachable = openWhenReady
        Task {
            if await Self.probe(urlString: healthURL) {
                localHTTPReachable = true
                state = .running
                appendLog("检测到已有本机服务，直接复用。")
                if openWhenReady {
                    open(localURL)
                    shouldOpenWhenReachable = false
                }
                return
            }
            launchProcess()
        }
    }

    func restartServices() {
        guard canRestartServices else {
            return
        }
        shouldOpenWhenReachable = true
        if let process, process.isRunning {
            shouldStartAfterStop = true
            state = .restarting
            appendLog("正在重启服务...")
            process.terminate()
        } else {
            appendLog("没有由启动台启动的进程，正在重新启动服务。")
            startServices(openWhenReady: true)
        }
    }

    func stopServices() {
        guard let process, process.isRunning else {
            state = localHTTPReachable ? .running : .stopped
            appendLog("没有由启动台启动的进程可停止。")
            return
        }
        shouldStartAfterStop = false
        state = .stopping
        appendLog("正在停止服务...")
        process.terminate()
    }

    func refreshStatus() {
        Task {
            let ok = await Self.probe(urlString: healthURL)
            handleHealth(ok)
            appendLog(ok ? "健康检查通过。" : "健康检查未连通。")
        }
    }

    func open(_ urlString: String) {
        guard let url = URL(string: urlString) else {
            return
        }
        NSWorkspace.shared.open(url)
    }

    func copy(_ urlString: String) {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(urlString, forType: .string)
        lastCopiedURL = urlString
        appendLog("已复制地址：\(urlString)")
    }

    func revealProjectRoot() {
        NSWorkspace.shared.activateFileViewerSelecting([projectRoot])
    }

    func revealLogFile() {
        NSWorkspace.shared.activateFileViewerSelecting([logFileURL])
    }

    func copyLogFilePath() {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(logFileURL.path, forType: .string)
        lastCopiedURL = logFileURL.path
        appendLog("已复制日志路径：\(logFileURL.path)")
    }

    func clearLog() {
        logText = ""
    }

    func stopAllServices() {
        stopServices()
        healthTask?.cancel()
        healthTask = nil
    }

    private var healthURL: String {
        "\(localURL)health"
    }

    private var pythonExecutable: String {
        let environment = ProcessInfo.processInfo.environment
        if let explicitPython = environment["SPECTRAL_WORKBENCH_PYTHON"],
           FileManager.default.isExecutableFile(atPath: explicitPython) {
            return explicitPython
        }
        let candidates = [
            "/opt/miniconda3/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "/usr/bin/python3"
        ]
        return candidates.first { FileManager.default.isExecutableFile(atPath: $0) } ?? "/usr/bin/python3"
    }

    private func launchProcess() {
        let apiFile = projectRoot.appendingPathComponent("packages/spectral_core/src/spectral_core/api/app.py")
        guard FileManager.default.fileExists(atPath: apiFile.path) else {
            state = .failed
            appendLog("未找到平台 API 文件：\(apiFile.path)")
            return
        }

        state = .starting
        localHTTPReachable = false
        appendLog("")
        appendLog("正在启动本机 FastAPI 工作台...")
        appendLog("Python：\(pythonExecutable)")

        let process = Process()
        let pipe = Pipe()
        process.executableURL = URL(fileURLWithPath: pythonExecutable)
        process.arguments = [
            "-m", "uvicorn",
            "spectral_core.api.app:create_app",
            "--factory",
            "--host", "127.0.0.1",
            "--port", "8765"
        ]
        process.currentDirectoryURL = projectRoot
        var environment = ProcessInfo.processInfo.environment
        environment["PYTHONUNBUFFERED"] = "1"
        environment["PYTHONPATH"] = projectRoot.appendingPathComponent("packages/spectral_core/src").path
        environment["PATH"] = [
            "/opt/miniconda3/bin",
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin",
            "/usr/sbin",
            "/sbin"
        ].joined(separator: ":")
        process.environment = environment
        process.standardOutput = pipe
        process.standardError = pipe

        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty, let text = String(data: data, encoding: .utf8) else {
                return
            }
            Task { @MainActor in
                self?.appendLog(text)
            }
        }

        process.terminationHandler = { [weak self] process in
            Task { @MainActor in
                self?.handleTermination(status: process.terminationStatus)
            }
        }

        do {
            try process.run()
            self.process = process
            self.outputPipe = pipe
            startHealthChecks()
        } catch {
            state = .failed
            appendLog("启动失败：\(error.localizedDescription)")
        }
    }

    private func startHealthChecks() {
        healthTask?.cancel()
        healthTask = Task { [weak self] in
            while !Task.isCancelled {
                guard let self else {
                    return
                }
                let ok = await Self.probe(urlString: self.healthURL)
                await MainActor.run {
                    self.handleHealth(ok)
                }
                try? await Task.sleep(nanoseconds: 1_500_000_000)
            }
        }
    }

    private func handleHealth(_ ok: Bool) {
        localHTTPReachable = ok
        if ok {
            if state == .starting || state == .restarting || state == .stopped {
                state = .running
                appendLog("本机工作台已就绪：\(localURL)")
            }
            if shouldOpenWhenReachable {
                open(localURL)
                shouldOpenWhenReachable = false
            }
        } else if state == .running && !isOwnedProcessActive {
            state = .stopped
        }
    }

    private func handleTermination(status: Int32) {
        outputPipe?.fileHandleForReading.readabilityHandler = nil
        process = nil
        outputPipe = nil
        localHTTPReachable = false

        if shouldStartAfterStop {
            shouldStartAfterStop = false
            appendLog("服务已停止，准备重新启动。")
            startServices(openWhenReady: shouldOpenWhenReachable)
            return
        }

        if status == 0 || state == .stopping {
            state = .stopped
            appendLog("服务已停止。")
        } else {
            state = .failed
            appendLog("服务异常退出，状态码：\(status)")
        }
    }

    private func appendLog(_ text: String) {
        let normalized = text.hasSuffix("\n") || text.isEmpty ? text : "\(text)\n"
        logText += normalized
        if logText.count > 60_000 {
            logText.removeFirst(logText.count - 60_000)
        }
        appendToLogFile(normalized)
    }

    private func prepareLogFile() {
        let directory = logFileURL.deletingLastPathComponent()
        do {
            try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
            if !FileManager.default.fileExists(atPath: logFileURL.path) {
                FileManager.default.createFile(atPath: logFileURL.path, contents: nil)
            }
        } catch {
            logText += "无法创建日志文件：\(error.localizedDescription)\n"
        }
    }

    private func appendToLogFile(_ text: String) {
        guard !text.isEmpty, let data = text.data(using: .utf8) else {
            return
        }
        do {
            let handle = try FileHandle(forWritingTo: logFileURL)
            try handle.seekToEnd()
            try handle.write(contentsOf: data)
            try handle.close()
        } catch {
            logText += "无法写入日志文件：\(error.localizedDescription)\n"
        }
    }

    nonisolated private static func probe(urlString: String) async -> Bool {
        guard let url = URL(string: urlString) else {
            return false
        }
        var request = URLRequest(url: url)
        request.timeoutInterval = 1.2
        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse else {
                return false
            }
            return (200..<300).contains(http.statusCode)
        } catch {
            return false
        }
    }
}
