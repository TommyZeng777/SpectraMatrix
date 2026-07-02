import Foundation

struct LauncherEndpoint: Identifiable, Hashable {
    let id: String
    let title: String
    let subtitle: String
    let url: String
    let note: String
    let symbolName: String
}

enum LauncherRunState: String {
    case stopped
    case starting
    case running
    case restarting
    case stopping
    case failed

    var title: String {
        switch self {
        case .stopped:
            return "已停止"
        case .starting:
            return "启动中"
        case .running:
            return "运行中"
        case .restarting:
            return "重启中"
        case .stopping:
            return "停止中"
        case .failed:
            return "需要处理"
        }
    }

    var systemImage: String {
        switch self {
        case .stopped:
            return "power"
        case .starting:
            return "hourglass"
        case .running:
            return "checkmark.circle.fill"
        case .restarting:
            return "arrow.clockwise.circle"
        case .stopping:
            return "stop.circle"
        case .failed:
            return "exclamationmark.triangle.fill"
        }
    }
}
