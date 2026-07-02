import AppKit
import SwiftUI

@main
struct SpectralMatrixLauncherApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @StateObject private var store = LauncherStore()

    var body: some Scene {
        WindowGroup("光谱训练矩阵", id: "main") {
            ContentView(store: store)
                .task {
                    store.startOnLaunch()
                }
                .onReceive(NotificationCenter.default.publisher(for: NSApplication.willTerminateNotification)) { _ in
                    store.stopAllServices()
                }
        }
        .defaultSize(width: 860, height: 640)
        .commands {
            CommandGroup(after: .newItem) {
                Button("启动并打开") {
                    store.startAndOpen()
                }
                .keyboardShortcut("r", modifiers: [.command])
                .disabled(!store.localHTTPReachable && !store.canStartServices)

                Button("重启服务") {
                    store.restartServices()
                }
                .keyboardShortcut("r", modifiers: [.command, .shift])
                .disabled(!store.canRestartServices)

                Button("停止服务") {
                    store.stopServices()
                }
                .keyboardShortcut(".", modifiers: [.command])
                .disabled(!store.canStopServices)
            }
        }

        MenuBarExtra {
            Button("打开工作台") {
                store.open(store.localURL)
            }
            Button("启动并打开") {
                store.startAndOpen()
            }
            .disabled(!store.localHTTPReachable && !store.canStartServices)
            Button("停止服务") {
                store.stopServices()
            }
            .disabled(!store.canStopServices)
        } label: {
            Label("光谱矩阵", systemImage: store.localHTTPReachable ? "checkmark.circle.fill" : "circle")
        }
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        NSApp.activate(ignoringOtherApps: true)
    }
}
