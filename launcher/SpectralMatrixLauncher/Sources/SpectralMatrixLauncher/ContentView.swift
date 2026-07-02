import AppKit
import SwiftUI

struct ContentView: View {
    @ObservedObject var store: LauncherStore

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            header

            HStack(alignment: .top, spacing: 16) {
                servicePanel
                quickActionsPanel
            }

            logPanel
        }
        .padding(22)
        .frame(minWidth: 760, minHeight: 560)
    }

    private var header: some View {
        HStack(alignment: .center, spacing: 14) {
            launcherLogo
            .frame(width: 56, height: 56)

            VStack(alignment: .leading, spacing: 4) {
                Text("光谱训练矩阵启动台")
                    .font(.title2.weight(.semibold))
                Text("本地 FastAPI 工作台 · 1D-CNN 全因子训练矩阵")
                    .font(.callout)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            statusBadge
        }
    }

    @ViewBuilder
    private var launcherLogo: some View {
        if let logoImage = NSImage(named: "AppIcon-80") {
            Image(nsImage: logoImage)
                .resizable()
                .scaledToFit()
                .clipShape(RoundedRectangle(cornerRadius: 13, style: .continuous))
        } else {
            ZStack {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(Color.accentColor.opacity(0.16))
                Image(systemName: "waveform.path.ecg.rectangle")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(Color.accentColor)
            }
        }
    }

    private var statusBadge: some View {
        Label(store.localHTTPReachable ? "服务可访问" : store.state.title, systemImage: store.localHTTPReachable ? "checkmark.circle.fill" : store.state.systemImage)
            .font(.callout.weight(.semibold))
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .foregroundStyle(store.localHTTPReachable ? Color.green : Color.secondary)
            .background((store.localHTTPReachable ? Color.green : Color.secondary).opacity(0.12), in: Capsule())
    }

    private var servicePanel: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label("启动访问", systemImage: "bolt.fill")
                .font(.headline)

            endpointCard(store.endpoint)

            HStack(spacing: 10) {
                Button {
                    store.startAndOpen()
                } label: {
                    Label(store.localHTTPReachable ? "打开工作台" : "启动并打开", systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(!store.localHTTPReachable && !store.canStartServices)

                Button {
                    store.restartServices()
                } label: {
                    Label("重启", systemImage: "arrow.clockwise")
                }
                .disabled(!store.canRestartServices)

                Button {
                    store.stopServices()
                } label: {
                    Label("停止", systemImage: "stop.fill")
                }
                .disabled(!store.canStopServices)
            }

            Text("启动台只包含当前平台已有能力：本机 API、浏览器工作台、日志与健康检查。")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .panelStyle()
    }

    private var quickActionsPanel: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label("快捷操作", systemImage: "switch.2")
                .font(.headline)

            actionButton("刷新状态", systemImage: "arrow.clockwise") {
                store.refreshStatus()
            }

            actionButton("打开工作台", systemImage: "safari") {
                store.open(store.localURL)
            }

            actionButton("复制地址", systemImage: "doc.on.doc") {
                store.copy(store.localURL)
            }

            actionButton("显示项目目录", systemImage: "folder") {
                store.revealProjectRoot()
            }

            actionButton("打开日志文件", systemImage: "doc.text.magnifyingglass") {
                store.revealLogFile()
            }

            actionButton("复制日志路径", systemImage: "link") {
                store.copyLogFilePath()
            }

            Divider()

            Text(store.projectRootPath)
                .font(.caption2.monospaced())
                .foregroundStyle(.secondary)
                .lineLimit(3)

            Text(store.logFilePath)
                .font(.caption2.monospaced())
                .foregroundStyle(.secondary)
                .lineLimit(2)
        }
        .panelStyle()
        .frame(width: 280)
    }

    private func endpointCard(_ endpoint: LauncherEndpoint) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 10) {
                Image(systemName: endpoint.symbolName)
                    .font(.title3)
                    .foregroundStyle(Color.accentColor)
                    .frame(width: 26)

                VStack(alignment: .leading, spacing: 2) {
                    Text(endpoint.title)
                        .font(.headline)
                    Text(endpoint.subtitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Spacer()
            }

            Text(endpoint.url)
                .font(.body.monospaced())
                .textSelection(.enabled)

            Text(endpoint.note)
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .background(Color.secondary.opacity(0.08), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .strokeBorder(Color.secondary.opacity(0.14))
        }
    }

    private func actionButton(_ title: String, systemImage: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack {
                Label(title, systemImage: systemImage)
                Spacer()
            }
        }
        .buttonStyle(.bordered)
    }

    private var logPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Label("运行日志", systemImage: "terminal")
                    .font(.headline)
                Spacer()
                Button("清空") {
                    store.clearLog()
                }
            }

            ScrollView {
                Text(store.logText.isEmpty ? "暂无日志。" : store.logText)
                    .font(.system(.caption, design: .monospaced))
                    .foregroundStyle(.primary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .textSelection(.enabled)
                    .padding(12)
            }
            .background(Color.black.opacity(0.05), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .strokeBorder(Color.secondary.opacity(0.12))
            }
        }
        .frame(maxHeight: .infinity)
    }
}

private extension View {
    func panelStyle() -> some View {
        self
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .topLeading)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .strokeBorder(Color.secondary.opacity(0.14))
            }
    }
}
