// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "SpectralMatrixLauncher",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(name: "SpectralMatrixLauncher", targets: ["SpectralMatrixLauncher"])
    ],
    targets: [
        .executableTarget(name: "SpectralMatrixLauncher")
    ]
)
