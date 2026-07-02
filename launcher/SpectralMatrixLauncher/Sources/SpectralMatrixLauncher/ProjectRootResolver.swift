import Foundation

enum ProjectRootResolver {
    static func resolve() -> URL {
        let environment = ProcessInfo.processInfo.environment
        if let explicitRoot = environment["SPECTRAL_WORKBENCH_ROOT"], isProjectRoot(URL(fileURLWithPath: explicitRoot)) {
            return URL(fileURLWithPath: explicitRoot)
        }

        if let resourceRoot = Bundle.main.url(forResource: "project-root", withExtension: "txt"),
           let text = try? String(contentsOf: resourceRoot, encoding: .utf8) {
            let path = text.trimmingCharacters(in: .whitespacesAndNewlines)
            let url = URL(fileURLWithPath: path)
            if isProjectRoot(url) {
                return url
            }
        }

        if let nearest = nearestProjectRoot(from: Bundle.main.bundleURL) {
            return nearest
        }

        return URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
    }

    private static func nearestProjectRoot(from startURL: URL) -> URL? {
        var current = startURL
        for _ in 0..<8 {
            if isProjectRoot(current) {
                return current
            }
            current.deleteLastPathComponent()
        }
        return nil
    }

    private static func isProjectRoot(_ url: URL) -> Bool {
        let marker = url.appendingPathComponent("packages/spectral_core/src/spectral_core/api/app.py")
        return FileManager.default.fileExists(atPath: marker.path)
    }
}
