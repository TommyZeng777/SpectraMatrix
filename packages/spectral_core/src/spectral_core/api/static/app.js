const apiDot = document.querySelector("#api-dot");
const apiStatus = document.querySelector("#api-status");
const rootPath = document.querySelector("#root-path");
const resultRows = document.querySelector("#result-rows");
const jsonOutput = document.querySelector("#json-output");
const resultSummary = document.querySelector("#result-summary");
const taskSummary = document.querySelector("#task-summary");
const taskCounts = document.querySelector("#task-counts");
const taskRows = document.querySelector("#task-rows");
const taskLogKind = document.querySelector("#task-log-kind");
const taskLogPath = document.querySelector("#task-log-path");
const taskLogOutput = document.querySelector("#task-log-output");
const queueJobStatus = document.querySelector("#queue-job-status");
const queueStopButton = document.querySelector("#queue-stop");
const queueResumeButton = document.querySelector("#queue-resume");
const projectFilePath = document.querySelector("#project-file-path");
const projectFileInput = document.querySelector("#project-file-input");
const projectBrowseButton = document.querySelector("#project-browse");
const projectOpenDemoButton = document.querySelector("#project-open-demo");
const projectDropzone = document.querySelector("#project-dropzone");
const projectSelectedFile = document.querySelector("#project-selected-file");
const projectOpenButton = document.querySelector("#project-open");
const projectSaveButton = document.querySelector("#project-save");
const projectSaveAsButton = document.querySelector("#project-save-as");
const projectSaveDialog = document.querySelector("#project-save-dialog");
const projectSaveDialogTitle = document.querySelector("#project-save-dialog-title");
const projectSaveDialogHint = document.querySelector("#project-save-dialog-hint");
const projectSaveNameInput = document.querySelector("#project-save-name");
const projectSaveConfirm = document.querySelector("#project-save-confirm");
const projectSaveCancel = document.querySelector("#project-save-cancel");
const projectStatus = document.querySelector("#project-status");
const languageToggle = document.querySelector("#language-toggle");
const spectraDropzone = document.querySelector("#spectra-dropzone");
const spectraFileInput = document.querySelector("#spectra-file-input");
const spectraBrowse = document.querySelector("#spectra-browse");
const spectraSelected = document.querySelector("#spectra-selected");
const supervisionDropzone = document.querySelector("#supervision-dropzone");
const supervisionFileInput = document.querySelector("#supervision-file-input");
const supervisionBrowse = document.querySelector("#supervision-browse");
const supervisionSelected = document.querySelector("#supervision-selected");
const importDemoDataset = document.querySelector("#import-demo-dataset");
const importStart = document.querySelector("#import-start");
const importSelectionStatus = document.querySelector("#import-selection-status");
const importSummary = document.querySelector("#import-summary");
const datasetCheckMessage = document.querySelector("#dataset-check-message");
const matrixStatus = document.querySelector("#matrix-status");
const matrixResult = document.querySelector("#matrix-result");
const matrixResultTitle = document.querySelector("#matrix-result-title");
const matrixResultDetail = document.querySelector("#matrix-result-detail");
const matrixGoQueue = document.querySelector("#matrix-go-queue");
const matrixGoMonitor = document.querySelector("#matrix-go-monitor");
const matrixExport = document.querySelector("#matrix-export");
const matrixCreatedTaskBlocks = document.querySelector("#matrix-created-task-blocks");
const matrixTotal = document.querySelector("#matrix-total");
const matrixFormula = document.querySelector("#matrix-formula");
const matrixGridList = document.querySelector("#matrix-grid-list");
const matrixFixedList = document.querySelector("#matrix-fixed-list");
const factorialRows = document.querySelector("#factorial-rows");
const factorialDraftTotal = document.querySelector("#factorial-draft-total");
const factorialStatus = document.querySelector("#factorial-status");
const factorialModeList = document.querySelector("#factorial-mode-list");
const factorialAdd = document.querySelector("#factorial-add");
const factorialReset = document.querySelector("#factorial-reset");
const factorialApply = document.querySelector("#factorial-apply");
const datasetCodeInput = document.querySelector("#dataset-code-input");
const datasetConfirm = document.querySelector("#dataset-confirm");
const datasetLockStatus = document.querySelector("#dataset-lock-status");
const activeDatasetCode = document.querySelector("#active-dataset-code");
const taskBlocks = document.querySelector("#task-blocks");
const targetToggles = document.querySelectorAll("[data-target-toggle]");
const targetRuleEmpty = document.querySelector("#target-rule-empty");
const splitModeInputs = document.querySelectorAll("input[name='split_mode']");
const splitModeList = document.querySelector("#split-mode-list");
const cvFoldPanel = document.querySelector("#cv-fold-panel");
const cvFoldOptions = document.querySelector("#cv-fold-options");
const splitTrainRatio = document.querySelector("#split-train-ratio");
const splitValRatio = document.querySelector("#split-val-ratio");
const splitTestRatio = document.querySelector("#split-test-ratio");
const trainingFramework = document.querySelector("#training-framework");
const trainingDevice = document.querySelector("#training-device");
const trainingPrecision = document.querySelector("#training-precision");
const trainingExportTarget = document.querySelector("#training-export-target");
const binaryThreshold = document.querySelector("#binary-threshold");
const triLowMax = document.querySelector("#tri-low-max");
const triMidMax = document.querySelector("#tri-mid-max");
const logOrbToggle = document.querySelector("#log-orb-toggle");
const logOrbPanel = document.querySelector("#log-orb-panel");
const logOrbCount = document.querySelector("#log-orb-count");
const logOrbSummary = document.querySelector("#log-orb-summary");
const logOrbEvents = document.querySelector("#log-orb-events");
const logOrbCopy = document.querySelector("#log-orb-copy");
const logOrbClear = document.querySelector("#log-orb-clear");
const logRecorderPath = document.querySelector("#log-recorder-path");
const logRecorderStart = document.querySelector("#log-recorder-start");
const logRecorderStop = document.querySelector("#log-recorder-stop");
const logRecorderStatus = document.querySelector("#log-recorder-status");
const outputDatasetCode = document.querySelector("#output-dataset-code");
const outputRegistryPath = document.querySelector("#output-registry-path");
const outputModelPicker = document.querySelector("#output-model-picker");
const outputChart = document.querySelector("#output-chart");
const outputChartPoints = document.querySelector("#output-chart-points");
const outputChartTitle = document.querySelector("#output-chart-title");
const outputMetricMainLabel = document.querySelector("#output-metric-main-label");
const outputMetricMain = document.querySelector("#output-metric-main");
const outputMetricSecondaryLabel = document.querySelector("#output-metric-secondary-label");
const outputMetricSecondary = document.querySelector("#output-metric-secondary");
const outputMetricTertiaryLabel = document.querySelector("#output-metric-tertiary-label");
const outputMetricTertiary = document.querySelector("#output-metric-tertiary");
const outputDetailList = document.querySelector("#output-detail-list");
const resultTaskSource = document.querySelector("#result-task-source");
const resultRegistrySource = document.querySelector("#result-registry-source");
const resultSelectionState = document.querySelector("#result-selection-state");
const resultsUseCurrent = document.querySelector("#results-use-current");
const metricChoices = document.querySelectorAll("[data-metric-choice]");
const topChoices = document.querySelectorAll("[data-top-choice]");
const workshopMlpLayers = document.querySelector("#workshop-mlp-layers");
const workshopHiddenWidth = document.querySelector("#workshop-hidden-width");
const workshopActivation = document.querySelector("#workshop-activation");
const workshopDropout = document.querySelector("#workshop-dropout");
const workshopCurrentPlan = document.querySelector("#workshop-current-plan");

let queueJobPoller = null;
let currentLanguage = localStorage.getItem("spectral_workbench_language") || "zh";
let currentMatrixPreview = null;
let factorialTouched = false;
let activeDataset = JSON.parse(localStorage.getItem("spectramatrix_active_dataset") || "null");
let workspaceState = JSON.parse(localStorage.getItem("spectramatrix_workspace_state") || "{}");
let activeQueueJobId = workspaceState.queueJobId || "";
let selectedOutputTaskId = workspaceState.selectedOutputTaskId || "";
let projectAutosaveTimer = null;
let pendingProjectSaveMode = "save";
let demoProjectPath = "";
let diagnosticsEvents = JSON.parse(localStorage.getItem("spectramatrix_diagnostics_events") || "[]");
let diagnosticsRecording = JSON.parse(localStorage.getItem("spectramatrix_diagnostics_recording") || "null");
const selectedImportFiles = {
  spectra: null,
  supervision: null,
};
const TARGET_TASK_VALUES = {
  regression: "ppm",
  binary: "binary",
  tri: "tri",
};

const FACTOR_CATALOG = [
  {
    key: "cv_fold",
    label: { zh: "交叉验证折", en: "CV fold" },
    candidates: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    presets: [
      { id: "folds_1_2", label: { zh: "快速 2 折", en: "Quick 2 folds" }, values: [1, 2] },
      { id: "folds_1_5", label: { zh: "完整 5 折", en: "Full 5 folds" }, values: [1, 2, 3, 4, 5] },
    ],
  },
  {
    key: "activation_id",
    label: { zh: "激活函数", en: "Activation" },
    candidates: ["relu", "gelu", "silu", "elu", "leaky_relu"],
    presets: [
      { id: "relu_gelu", label: { zh: "ReLU + GELU", en: "ReLU + GELU" }, values: ["relu", "gelu"] },
      { id: "relu_gelu_silu", label: { zh: "ReLU + GELU + SiLU", en: "ReLU + GELU + SiLU" }, values: ["relu", "gelu", "silu"] },
      { id: "activation_all", label: { zh: "全部已支持激活", en: "All supported activations" }, values: ["relu", "gelu", "silu", "elu", "leaky_relu"] },
    ],
  },
  {
    key: "window_id",
    label: { zh: "光谱窗口", en: "Spectral window" },
    candidates: [
      "WFULL_500_2500",
      "AUTO5_1",
      "AUTO5_2",
      "AUTO5_3",
      "AUTO5_4",
      "AUTO5_5",
    ],
    presets: [
      { id: "window_full_only", label: { zh: "全谱窗口", en: "Full spectrum" }, values: ["WFULL_500_2500"] },
      { id: "window_auto5", label: { zh: "自动等分 5 段", en: "Auto split into 5 windows" }, values: ["AUTO5_1", "AUTO5_2", "AUTO5_3", "AUTO5_4", "AUTO5_5"] },
    ],
  },
  {
    key: "dropout",
    label: { zh: "Dropout", en: "Dropout" },
    candidates: [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5],
    presets: [
      { id: "dropout_safe", label: { zh: "常用 0.1 / 0.2", en: "Common 0.1 / 0.2" }, values: [0.1, 0.2] },
      { id: "dropout_wide", label: { zh: "扩展 0.1 / 0.2 / 0.35", en: "Wide 0.1 / 0.2 / 0.35" }, values: [0.1, 0.2, 0.35] },
      { id: "dropout_dense", label: { zh: "密集 0-0.5", en: "Dense 0-0.5" }, values: [0, 0.1, 0.2, 0.3, 0.4, 0.5] },
    ],
  },
  {
    key: "learning_rate",
    label: { zh: "学习率", en: "Learning rate" },
    candidates: [0.003, 0.001, 0.0007, 0.0005, 0.0003, 0.0001, 0.00005],
    presets: [
      { id: "lr_standard", label: { zh: "标准 1e-3 / 3e-4", en: "Standard 1e-3 / 3e-4" }, values: [0.001, 0.0003] },
      { id: "lr_wide", label: { zh: "扩展 1e-3 / 5e-4 / 3e-4", en: "Wide 1e-3 / 5e-4 / 3e-4" }, values: [0.001, 0.0005, 0.0003] },
      { id: "lr_dense", label: { zh: "密集学习率池", en: "Dense learning-rate pool" }, values: [0.003, 0.001, 0.0007, 0.0005, 0.0003, 0.0001] },
    ],
  },
  {
    key: "weight_decay",
    label: { zh: "权重衰减", en: "Weight decay" },
    candidates: [0.0, 0.000001, 0.00001, 0.00005, 0.0001, 0.0005, 0.001],
    presets: [
      { id: "wd_light", label: { zh: "无 / 1e-4", en: "None / 1e-4" }, values: [0.0, 0.0001] },
      { id: "wd_wide", label: { zh: "无 / 1e-5 / 1e-4", en: "None / 1e-5 / 1e-4" }, values: [0.0, 0.00001, 0.0001] },
      { id: "wd_dense", label: { zh: "密集正则池", en: "Dense regularization pool" }, values: [0.0, 0.000001, 0.00001, 0.00005, 0.0001, 0.0005] },
    ],
  },
  {
    key: "model_id",
    label: { zh: "1D-CNN 结构", en: "1D-CNN architecture" },
    candidates: ["cnn3", "cnn4", "dilated_cnn4"],
    presets: [
      { id: "cnn_basic", label: { zh: "轻量三层 / 标准四层", en: "Light 3-layer / standard 4-layer" }, values: ["cnn3", "cnn4"] },
      { id: "cnn_plus_dilated", label: { zh: "三层 / 四层 / 大感受野四层", en: "3-layer / 4-layer / wide-field 4-layer" }, values: ["cnn3", "cnn4", "dilated_cnn4"] },
    ],
  },
  {
    key: "pooling_id",
    label: { zh: "池化策略", en: "Pooling" },
    candidates: ["POOL0", "POOL2", "POOL3"],
    presets: [
      { id: "pool_common", label: { zh: "基础 / 双池化", en: "Baseline / dual pooling" }, values: ["POOL0", "POOL3"] },
      { id: "pool_all", label: { zh: "基础 / 大感受野 / 双池化", en: "Baseline / wide-field / dual pooling" }, values: ["POOL0", "POOL2", "POOL3"] },
    ],
  },
  {
    key: "preprocess_id",
    label: { zh: "光谱预处理", en: "Preprocess" },
    candidates: ["none", "raw_standard", "snv_standard"],
    presets: [
      { id: "prep_raw_snv", label: { zh: "原始标准化 / SNV 标准化", en: "Raw standardization / SNV standardization" }, values: ["raw_standard", "snv_standard"] },
      { id: "prep_with_none", label: { zh: "不处理 / 原始标准化 / SNV 标准化", en: "None / raw standardization / SNV standardization" }, values: ["none", "raw_standard", "snv_standard"] },
    ],
  },
  {
    key: "augmentation_id",
    label: { zh: "数据增强方法", en: "Data augmentation method" },
    candidates: ["AUG0", "AUG1", "AUG2", "AUG3", "AUG4"],
    presets: [
      { id: "aug_none", label: { zh: "不使用增强", en: "No augmentation" }, values: ["AUG0"] },
      { id: "aug_light", label: { zh: "不增强 / 加噪增强", en: "None / noise injection" }, values: ["AUG0", "AUG1"] },
      { id: "aug_spectral_common", label: { zh: "常用光谱增强组合", en: "Common spectral augmentation set" }, values: ["AUG0", "AUG1", "AUG2", "AUG3"] },
      { id: "aug_all", label: { zh: "全部增强方法", en: "All augmentation methods" }, values: ["AUG0", "AUG1", "AUG2", "AUG3", "AUG4"] },
    ],
  },
  {
    key: "augmentation_multiplier",
    label: { zh: "数据增强倍数", en: "Augmentation multiplier" },
    candidates: [1, 2, 3, 4, 5],
    presets: [
      { id: "aug_mult_off", label: { zh: "不扩增", en: "No expansion" }, values: [1] },
      { id: "aug_mult_light", label: { zh: "轻量 1× / 2×", en: "Light 1x / 2x" }, values: [1, 2] },
      { id: "aug_mult_wide", label: { zh: "扩展 1× / 2× / 3×", en: "Wide 1x / 2x / 3x" }, values: [1, 2, 3] },
    ],
  },
  {
    key: "batch_size",
    label: { zh: "Batch size", en: "Batch size" },
    candidates: [8, 16, 24, 32, 48, 64, 96, 128],
    presets: [
      { id: "batch_16_32", label: { zh: "16 / 32", en: "16 / 32" }, values: [16, 32] },
      { id: "batch_16_32_64", label: { zh: "16 / 32 / 64", en: "16 / 32 / 64" }, values: [16, 32, 64] },
    ],
  },
  {
    key: "seed",
    label: { zh: "随机种子", en: "Seed" },
    candidates: [20260616, 20260617, 20260618, 20260704, 20260705, 20260706],
    presets: [
      { id: "seed_one", label: { zh: "单种子", en: "Single seed" }, values: [20260616] },
      { id: "seed_three", label: { zh: "三种子稳定性", en: "Three-seed stability" }, values: [20260616, 20260617, 20260618] },
    ],
  },
  {
    key: "kernel_size",
    label: { zh: "卷积核大小", en: "Kernel size" },
    candidates: [3, 5, 7, 9, 11, 15],
    presets: [
      { id: "kernel_common", label: { zh: "3 / 5 / 7", en: "3 / 5 / 7" }, values: [3, 5, 7] },
      { id: "kernel_wide", label: { zh: "3 / 5 / 7 / 9 / 11", en: "3 / 5 / 7 / 9 / 11" }, values: [3, 5, 7, 9, 11] },
    ],
  },
  {
    key: "epochs",
    label: { zh: "训练轮数", en: "Epochs" },
    candidates: [2, 5, 10, 20, 40, 80, 120],
    presets: [
      { id: "epochs_smoke", label: { zh: "冒烟 2 / 5", en: "Smoke 2 / 5" }, values: [2, 5] },
      { id: "epochs_train", label: { zh: "正式 40 / 80 / 120", en: "Training 40 / 80 / 120" }, values: [40, 80, 120] },
    ],
  },
  {
    key: "target_transform",
    label: { zh: "回归目标变换", en: "Target transform" },
    candidates: ["linear", "log1p", "sqrt"],
    presets: [
      { id: "target_linear", label: { zh: "不变换", en: "No transform" }, values: ["linear"] },
      { id: "target_all", label: { zh: "不变换 / 对数 / 平方根", en: "None / log / square-root" }, values: ["linear", "log1p", "sqrt"] },
    ],
  },
  {
    key: "loss_id",
    label: { zh: "损失函数", en: "Loss function" },
    candidates: ["mse", "smoothl1"],
    presets: [
      { id: "loss_smoothl1", label: { zh: "Smooth L1", en: "Smooth L1" }, values: ["smoothl1"] },
      { id: "loss_regression_safe", label: { zh: "MSE / Smooth L1", en: "MSE / Smooth L1" }, values: ["mse", "smoothl1"] },
    ],
  },
  {
    key: "channels",
    label: { zh: "卷积通道", en: "Channels" },
    candidates: [[16, 32, 64], [32, 64, 128], [16, 32, 64, 128], [32, 64, 128, 256]],
    presets: [
      { id: "channels_light", label: { zh: "轻量/标准", en: "Light / standard" }, values: [[16, 32, 64], [32, 64, 128]] },
      { id: "channels_deep", label: { zh: "四层通道", en: "Four-layer channels" }, values: [[16, 32, 64, 128], [32, 64, 128, 256]] },
    ],
  },
];

const FACTORIAL_MODES = [
  {
    id: "quick",
    label: { zh: "快速验证", en: "Quick Check" },
    note: { zh: "小矩阵，确认数据和任务脚本能跑通。", en: "Small matrix to confirm data and task scripts." },
    factors: [
      { key: "activation_id", preset: "relu_gelu" },
      { key: "loss_id", preset: "loss_smoothl1" },
    ],
  },
  {
    id: "screening",
    label: { zh: "常规筛选", en: "Routine Screening" },
    note: { zh: "覆盖自动等分窗口、激活函数、dropout 和学习率。", en: "Covers auto-split windows, activation, dropout, and learning rate." },
    factors: [
      { key: "window_id", preset: "window_auto5" },
      { key: "augmentation_id", preset: "aug_light" },
      { key: "activation_id", preset: "relu_gelu" },
      { key: "dropout", preset: "dropout_safe" },
      { key: "learning_rate", preset: "lr_standard" },
      { key: "loss_id", preset: "loss_regression_safe" },
    ],
  },
  {
    id: "architecture",
    label: { zh: "网络结构加强", en: "Architecture Study" },
    note: { zh: "重点比较 CNN 结构、池化和激活函数。", en: "Focuses on CNN architecture, pooling, and activation." },
    factors: [
      { key: "model_id", preset: "cnn_plus_dilated" },
      { key: "pooling_id", preset: "pool_common" },
      { key: "activation_id", preset: "relu_gelu_silu" },
      { key: "loss_id", preset: "loss_regression_safe" },
    ],
  },
  {
    id: "augmentation",
    label: { zh: "数据增强研究", en: "Augmentation Study" },
    note: { zh: "比较加噪、基线扰动、小幅位移与组合增强，并可同时测试增强倍数。", en: "Compares noise, baseline perturbation, small shifts, combined augmentation, and expansion strength." },
    factors: [
      { key: "augmentation_id", preset: "aug_all" },
      { key: "augmentation_multiplier", preset: "aug_mult_wide" },
      { key: "preprocess_id", preset: "prep_raw_snv" },
      { key: "loss_id", preset: "loss_regression_safe" },
    ],
  },
];

const PARAM_KEY_LABELS = {
  activation: { zh: "激活函数", en: "Activation" },
  activation_id: { zh: "激活函数", en: "Activation" },
  augmentation_id: { zh: "数据增强方法", en: "Data augmentation method" },
  augmentation_multiplier: { zh: "数据增强倍数", en: "Augmentation multiplier" },
  batch_size: { zh: "批大小", en: "Batch size" },
  channels: { zh: "卷积通道", en: "Channels" },
  cv_fold: { zh: "交叉验证折", en: "CV fold" },
  dropout: { zh: "Dropout", en: "Dropout" },
  epochs: { zh: "训练轮数", en: "Epochs" },
  kernel_size: { zh: "卷积核大小", en: "Kernel size" },
  learning_rate: { zh: "学习率", en: "Learning rate" },
  loss_id: { zh: "损失函数", en: "Loss" },
  max_epochs: { zh: "最大训练轮数", en: "Max epochs" },
  model_id: { zh: "1D-CNN 结构", en: "1D-CNN architecture" },
  pooling_id: { zh: "池化策略", en: "Pooling" },
  preprocess_id: { zh: "光谱预处理", en: "Preprocess" },
  seed: { zh: "随机种子", en: "Seed" },
  target_transform: { zh: "目标变换", en: "Target transform" },
  task: { zh: "任务类型", en: "Task type" },
  weight_decay: { zh: "权重衰减", en: "Weight decay" },
  window_id: { zh: "光谱窗口", en: "Spectral window" },
};

const PARAM_VALUE_LABELS = {
  augmentation_id: {
    AUG0: { zh: "不使用数据增强", en: "No augmentation" },
    AUG1: { zh: "加噪增强", en: "Noise injection" },
    AUG2: { zh: "基线扰动增强", en: "Baseline perturbation" },
    AUG3: { zh: "加噪 + 小幅波长位移", en: "Noise + small wavelength shift" },
    AUG4: { zh: "组合增强（加噪 + 基线扰动 + 位移）", en: "Combined augmentation (noise + baseline + shift)" },
  },
  augmentation_multiplier: {
    1: { zh: "1× 不扩增", en: "1x no expansion" },
    2: { zh: "2× 训练集扩增", en: "2x training-set expansion" },
    3: { zh: "3× 训练集扩增", en: "3x training-set expansion" },
    4: { zh: "4× 训练集扩增", en: "4x training-set expansion" },
    5: { zh: "5× 训练集扩增", en: "5x training-set expansion" },
  },
  activation_id: {
    relu: { zh: "ReLU", en: "ReLU" },
    gelu: { zh: "GELU", en: "GELU" },
    silu: { zh: "SiLU", en: "SiLU" },
    elu: { zh: "ELU", en: "ELU" },
    leaky_relu: { zh: "Leaky ReLU", en: "Leaky ReLU" },
  },
  loss_id: {
    default: { zh: "默认损失函数", en: "Default loss" },
    mse: { zh: "均方误差 MSE", en: "Mean squared error" },
    smoothl1: { zh: "Smooth L1 损失", en: "Smooth L1 loss" },
    cross_entropy: { zh: "交叉熵损失", en: "Cross-entropy loss" },
    cross_entropy_weighted: { zh: "加权交叉熵损失", en: "Weighted cross-entropy loss" },
    focal: { zh: "Focal loss", en: "Focal loss" },
  },
  model_id: {
    cnn3: { zh: "三层轻量 1D-CNN", en: "Light 3-layer 1D-CNN" },
    cnn4: { zh: "四层标准 1D-CNN", en: "Standard 4-layer 1D-CNN" },
    dilated_cnn4: { zh: "大感受野四层 1D-CNN", en: "Wide-field 4-layer 1D-CNN" },
  },
  pooling_id: {
    POOL0: { zh: "基础平均池化", en: "Baseline average pooling" },
    POOL1: { zh: "基础平均池化（历史兼容）", en: "Baseline average pooling (legacy)" },
    POOL2: { zh: "大感受野平均池化", en: "Wide-field average pooling" },
    POOL3: { zh: "平均+最大双池化", en: "Average + max dual pooling" },
  },
  preprocess_id: {
    none: { zh: "不做光谱预处理", en: "No spectral preprocessing" },
    raw_standard: { zh: "原始光谱标准化", en: "Raw spectral standardization" },
    snv_standard: { zh: "SNV 后标准化", en: "SNV then standardization" },
    sg_deriv1_standard: { zh: "一阶导数标准化", en: "First-derivative standardization" },
    msc_standard: { zh: "MSC 后标准化", en: "MSC then standardization" },
  },
  target_transform: {
    linear: { zh: "不变换", en: "No transform" },
    log1p: { zh: "log1p 对数变换", en: "log1p transform" },
    sqrt: { zh: "平方根变换", en: "Square-root transform" },
  },
  task: {
    binary: { zh: "二分类", en: "Binary classification" },
    tri: { zh: "三分类", en: "Three-class classification" },
    tri_class: { zh: "三分类", en: "Three-class classification" },
    ppm: { zh: "连续值回归", en: "Continuous regression" },
    regression: { zh: "连续值回归", en: "Continuous regression" },
  },
  window_id: {
    W_FULL: { zh: "全谱窗口", en: "Full-spectrum window" },
    WFULL_500_2500: { zh: "全谱窗口 500-2500 nm", en: "Full spectrum 500-2500 nm" },
    AUTO5_1: { zh: "自动等分第 1/5 段", en: "Auto split segment 1/5" },
    AUTO5_2: { zh: "自动等分第 2/5 段", en: "Auto split segment 2/5" },
    AUTO5_3: { zh: "自动等分第 3/5 段", en: "Auto split segment 3/5" },
    AUTO5_4: { zh: "自动等分第 4/5 段", en: "Auto split segment 4/5" },
    AUTO5_5: { zh: "自动等分第 5/5 段", en: "Auto split segment 5/5" },
    W1: { zh: "短波窗口 W1 860-1100 nm", en: "Short window W1 860-1100 nm" },
    W2: { zh: "短波窗口 W2 820-1059 nm", en: "Short window W2 820-1059 nm" },
    W3: { zh: "红外控制窗口 W3 780-2500 nm", en: "IR control window W3 780-2500 nm" },
    W3_IR_780_2500: { zh: "红外控制窗口 780-2500 nm", en: "IR control window 780-2500 nm" },
    W4: { zh: "长波候选窗口 W4 1860-2019 nm", en: "Long-wave candidate W4 1860-2019 nm" },
    W5: { zh: "长波候选窗口 W5 2180-2259 nm", en: "Long-wave candidate W5 2180-2259 nm" },
    W6: { zh: "扩展短波窗口 W6 820-1250 nm", en: "Extended short window W6 820-1250 nm" },
    W8: { zh: "长波探索窗口 W8 1800-2300 nm", en: "Long-wave exploratory window W8 1800-2300 nm" },
    WCORE3: { zh: "BiPLS 三段核心窗口", en: "BiPLS core three-interval window" },
    full_spectrum: { zh: "全谱窗口", en: "Full-spectrum window" },
    WBIPLS_SHORT: { zh: "BiPLS 优选短波窗口", en: "BiPLS selected short-window" },
    WMID3: { zh: "BiPLS 中波拼接窗口", en: "BiPLS mid-band stitched window" },
    WLONG6: { zh: "BiPLS 长波拼接窗口", en: "BiPLS long-wave stitched window" },
    WBIPLS13: { zh: "BiPLS 13 段联合窗口", en: "BiPLS 13-interval union window" },
  },
};

const PARAM_VALUE_ALIASES = {
  activation: "activation_id",
  model: "model_id",
  pool: "pooling_id",
  preprocess: "preprocess_id",
};

const STATUS_LABELS = {
  idle: { zh: "空闲", en: "Idle" },
  pending: { zh: "等待中", en: "Pending" },
  queued: { zh: "排队中", en: "Queued" },
  starting: { zh: "启动中", en: "Starting" },
  running: { zh: "运行中", en: "Running" },
  stopping: { zh: "正在停止", en: "Stopping" },
  cancelled: { zh: "已中断", en: "Stopped" },
  succeeded: { zh: "已完成", en: "Succeeded" },
  failed: { zh: "失败", en: "Failed" },
  skipped: { zh: "已跳过", en: "Skipped" },
  unknown: { zh: "未知", en: "Unknown" },
};

const forms = {
  dataset: document.querySelector("#dataset-form"),
  matrix: document.querySelector("#matrix-form"),
  queue: document.querySelector("#queue-form"),
  monitor: document.querySelector("#task-monitor-form"),
  scan: document.querySelector("#scan-form"),
  candidate: document.querySelector("#candidate-form"),
  aggregate: document.querySelector("#aggregate-form"),
};

const i18n = {
  zh: {
    "action.defaults": "默认配置",
    "advanced.paths": "高级路径",
    "aggregate.run": "生成参数对比",
    "aggregate.title": "参数组合对比",
    "app.title": "SpectraMatrix 光谱模型训练平台",
    "app.workspace": "工作区",
    "brand.subtitle": "本地工作台",
    "candidate.select": "筛选最佳模型",
    "candidate.title": "候选模型",
    "console.action": "动作",
    "console.clear": "清空",
    "console.empty": "运行一个动作后会显示结果。",
    "console.output": "关键输出",
    "console.status": "状态",
    "console.time": "时间",
    "console.title": "调试记录",
    "context.changeData": "更换数据",
    "context.dataset": "当前训练数据",
    "data.inspectCurrent": "检查当前数据",
    "data.subtitle": "下载模板，准备两张标准 CSV，拖入后自动检查 sample_link_code、PPM 监督值和可用训练数据。",
    "data.title": "导入并检查数据",
    "datasetCode.confirm": "确认使用此数据",
    "datasetCode.label": "训练数据代号",
    "datasetCode.locked": "已确认训练数据：",
    "datasetCode.needCode": "请填写训练数据代号。",
    "datasetCode.note": "导入检查通过后，为这批数据填写一个训练数据代号。这个代号会传递到模型训练设计、训练台、结果筛选、模型工坊和模型成果。",
    "datasetCode.ready": "导入检查通过。请填写训练数据代号。",
    "datasetCode.tag": "必填",
    "datasetCode.title": "确认训练数据",
    "datasetCode.waiting": "请先导入两张模板 CSV。",
    "datasetInspect.fail": "检查失败",
    "datasetInspect.idle": "导入两张 CSV 后会自动检查样品数、波长点和目标列。",
    "datasetInspect.noConfig": "还没有可检查的数据。请先导入光谱矩阵和监督标签。",
    "datasetInspect.run": "重新检查",
    "datasetInspect.success": "检查完成",
    "datasetInspect.tag": "自动",
    "datasetInspect.title": "数据检查结果",
    "field.aggregateOutput": "聚合输出",
    "field.candidateOutput": "候选输出",
    "field.configPath": "配置路径",
    "field.direction": "方向",
    "field.groupBy": "分组",
    "field.logType": "日志类型",
    "field.matrixConfig": "矩阵配置",
    "field.matrixOutput": "矩阵输出",
    "field.maxTasks": "本次最多执行（留空=全部）",
    "field.metric": "指标",
    "field.outputFolder": "输出文件夹",
    "field.registryCsv": "Registry CSV",
    "field.registryOutput": "结果表输出文件夹",
    "field.taskFolder": "任务文件夹",
    "field.top": "Top",
    "factorial.add": "添加预设因子",
    "factorial.apply": "应用全因子设计",
    "factorial.applied": "当前选择已同步，组合数已刷新。",
    "factorial.applying": "正在同步当前选择...",
    "factorial.count": "数量",
    "factorial.customPlaceholder": "自定义水平，如 0.0002 或 [16,32,64]",
    "factorial.customSelection": "自定义选择",
    "factorial.draftTotal": "草稿组合数",
    "factorial.duplicate": "因子不能重复：",
    "factorial.exhausted": "所有预设因子都已经在表中。",
    "factorial.emptyFactor": "请填写因子名。",
    "factorial.emptyLevels": "每个因子至少需要 1 个可选参数。",
    "factorial.factor": "因子（可调参数）",
    "factorial.fail": "全因子设计应用失败",
    "factorial.idle": "当前选择会在生成或导出时自动生效。",
    "factorial.levelPlaceholder": "例如：relu, gelu 或 0.1, 0.2",
    "factorial.levels": "可选参数（选中才参与）",
    "factorial.levelAdd": "添加参数",
    "factorial.levelParseFail": "无法解析自定义参数，请输入数字、文本或 JSON 数组。",
    "factorial.windowParseFail": "窗口格式应为 800-1100；拼接窗口可写 800-900;1000-1100。",
    "factorial.modeApplied": "推荐模式已载入，可直接生成训练矩阵。",
    "factorial.note": "从预设参数库选择因子和可选参数，系统自动穷举所有组合。",
    "factorial.preset": "推荐参数组",
    "factorial.remove": "移除",
    "factorial.title": "模型可选参数",
    "import.choose": "选择文件",
    "import.chooseSpectra": "选择光谱文件",
    "import.chooseSupervision": "选择监督文件",
    "import.demoDataset": "导入演示数据集",
    "import.empty": "尚未导入文件。",
    "import.help": "推荐直接导入 CSV 数据包：光谱宽表 + 监督标签表。NPZ 也支持；JSON 仅作为自动生成的高级配置。",
    "import.notSelected": "尚未选择",
    "import.downloadSpectraTemplate": "下载光谱数据模板",
    "import.downloadSupervisionTemplate": "下载监督数据模板",
    "import.readyPair": "两张文件已就绪，可以导入。",
    "import.spectraHelp": "拖入光谱宽表 CSV，或已有的光谱矩阵 NPZ。",
    "import.spectraTitle": "光谱矩阵",
    "import.start": "导入并检查",
    "import.supervisionHelp": "拖入监督数值 CSV，典型列为 sample_link_code 与 ppm_mg_kg。",
    "import.supervisionTitle": "监督标签",
    "import.title": "拖拽文件到这里",
    "import.waitingPair": "请选择光谱矩阵和监督标签两张文件。",
    "matrix.create": "生成训练矩阵",
    "matrix.createdDetail": "训练项目已经写入本地文件夹，可以打开到模型训练台执行。",
    "matrix.createdTitle": "已生成训练项目",
    "matrix.export": "导出训练矩阵文件包",
    "matrix.exportedTitle": "已导出训练矩阵文件包",
    "matrix.fixedEmpty": "没有固定参数",
    "matrix.fixedOnly": "无可调参数：1 个固定任务",
    "matrix.fixedTitle": "固定参数",
    "matrix.gridEmpty": "当前矩阵没有可调参数，只会生成 1 个固定任务。",
    "matrix.gridTitle": "可调参数候选值",
    "matrix.idle": "尚未生成训练项目。",
    "matrix.limit": "安全上限（可选）",
    "matrix.limitHelp": "它不是训练数量设置。若填写数字且低于组合总数，会阻止创建，用来避免误生成过大的任务矩阵。",
    "matrix.limitPlaceholder": "留空：生成全部组合",
    "matrix.limitTooLow": "安全上限低于组合总数，已阻止创建。请清空上限，或把它设为不小于组合总数。",
    "matrix.nextMonitor": "刷新任务块",
    "matrix.nextQueue": "打开到模型训练台",
    "matrix.note": "在这里完成训练环境、训练目标、数据划分和模型可选参数设置，然后生成可执行训练项目。",
    "matrix.presetAll": "不设上限",
    "matrix.presetSafety": "安全上限 10",
    "matrix.presetTotal": "设为组合总数",
    "matrix.previewFail": "矩阵预览失败",
    "matrix.previewIdle": "正在读取参数矩阵...",
    "matrix.previewLoading": "正在读取参数矩阵...",
    "matrix.previewReady": "当前矩阵组合总数",
    "matrix.previewTaskDetails": "子任务详情",
    "matrix.running": "正在按当前选择生成训练矩阵...",
    "matrix.step1": "1. 选择可选参数",
    "matrix.step1Note": "每个参数放入候选值",
    "matrix.step2": "2. 展开组合",
    "matrix.step2Note": "候选值做笛卡尔组合",
    "matrix.step3": "3. 生成任务",
    "matrix.step3Note": "每个组合输出一个脚本任务",
    "matrix.tag": "训练项目",
    "matrix.taskUnit": "个训练任务",
    "matrix.title": "模型训练设计",
    "matrix.totalLabel": "组合总数",
    "metric.samples": "样品",
    "metric.targets": "目标列",
    "metric.wavelengths": "波长点",
    "metric.windows": "窗口",
    "monitor.empty": "刷新任务文件夹以查看状态。",
    "monitor.refresh": "刷新任务",
    "monitor.selectTask": "选择一行任务查看日志。",
    "monitor.title": "任务进度",
    "nav.data": "数据导入",
    "nav.matrix": "模型训练设计",
    "nav.outputs": "模型成果",
    "nav.queue": "模型训练台",
    "nav.results": "结果筛选",
    "nav.workshop": "模型工坊",
    "outputs.note": "这里展示当前模型的训练成果。回归任务会显示预测值 vs 实测值、R2、RMSE、MAE 和残差图；分类任务显示混淆矩阵和每类指标。",
    "outputs.modelPicker": "选择要展示的模型",
    "outputs.regressionPlot": "预测值 vs 实测值",
    "outputs.tag": "图表与报告",
    "outputs.title": "模型成果",
    "project.autoSaveReady": "打开或保存工程后，才会自动保存到当前工程文件。",
    "project.advancedPath": "高级路径",
    "project.choose": "打开",
    "project.dropHint": "拖入 .spectramatrix.json，恢复数据、训练设计、队列和结果。",
    "project.dropTitle": "打开或继续工程",
    "project.file": "工程文件路径",
    "project.noFile": "尚未选择工程",
    "project.open": "打开工程",
    "project.openByPath": "按路径打开",
    "project.openDemo": "导入演示数据",
    "project.opened": "工程已打开，进度已恢复。",
    "project.save": "保存",
    "project.saveAs": "另存为",
    "project.saveAsSaved": "工程已另存为。",
    "project.saveDialogCancel": "取消",
    "project.saveDialogConfirm": "保存",
    "project.saveDialogHint": "输入一个容易识别的工程文件名，系统会保存为 .spectramatrix.json。",
    "project.saveDialogName": "工程文件名",
    "project.saveDialogTitle": "保存工程文件",
    "project.saveDialogTitleAs": "另存为新工程",
    "project.saveNeedName": "请填写工程文件名。",
    "project.saved": "工程已保存。",
    "project.sidebarTitle": "工作区工程",
    "queue.dryRun": "只检查脚本，不真正训练",
    "queue.note": "当前工程包含训练任务后，可以在这里执行、暂停、重跑失败任务，并用任务块查看训练进度。",
    "queue.rerunFailed": "重跑失败任务",
    "queue.resume": "继续训练",
    "queue.run": "开始训练",
    "queue.stop": "停止当前训练",
    "queue.tag": "训练项目",
    "queue.title": "模型训练台",
    "results.advancedRule": "高级：手动指标和输出路径",
    "results.aggregateNote": "想看哪类参数整体更好时再用，例如比较不同光谱窗口、模型结构或预处理方式。",
    "results.currentProject": "当前工程",
    "results.title": "结果筛选",
    "results.finalCandidate": "设为最终候选",
    "results.keepHowMany": "保留前几名",
    "results.metricBalancedAccuracy": "分类均衡准确率，越高越好",
    "results.metricMae": "平均绝对误差，越低越好",
    "results.metricRmse": "回归误差，越低越好",
    "results.optional": "可选",
    "results.readyState": "筛选状态",
    "results.resultTable": "结果表",
    "results.stepRule": "2. 选择筛选规则",
    "results.stepRuleNote": "回归任务通常看 RMSE 或 MAE，数值越低越好；分类任务通常看 balanced accuracy，越高越好。",
    "results.stepSource": "1. 读取训练结果",
    "results.stepSourceNote": "优先使用当前工程的训练任务和结果表；普通用户不需要填写路径。",
    "results.subtitle": "训练结束后，在这里读取当前训练结果，按指标挑出值得继续验证的模型组合。",
    "results.trainingTasks": "训练任务",
    "results.useCurrent": "使用当前训练结果",
    "scan.run": "扫描训练结果",
    "scan.title": "扫描运行结果",
    "table.activation": "激活",
    "table.fold": "Fold",
    "table.log": "日志",
    "table.metric": "指标",
    "table.model": "模型",
    "table.status": "状态",
    "table.task": "任务",
    "table.window": "窗口",
    "design.binary": "二分类筛查",
    "design.binaryNote": "由 PPM 阈值自动生成。",
    "design.binaryRule": "未超标：ppm < 阈值；超标：ppm ≥ 阈值",
    "design.binaryThreshold": "二分类阈值",
    "design.device": "运行设备",
    "design.envCheck": "检查训练环境",
    "design.envTitle": "训练环境",
    "design.exportTarget": "导出目标",
    "design.framework": "训练框架",
    "design.lowMax": "低风险上限",
    "design.midMax": "中风险上限",
    "design.precision": "训练精度",
    "design.ratio": "比例",
    "design.regression": "PPM 回归预测",
    "design.regressionNote": "直接预测连续 PPM。",
    "design.ruleTitle": "分类判别标准",
    "design.ruleEmpty": "当前只做连续值回归，不需要设置分类阈值。",
    "design.splitNote": "按 sample_link_code 分组划分，避免同一样品泄漏。",
    "design.splitTitle": "数据划分",
    "design.splitHoldout": "训练集 + 验证集 + 独立测试集",
    "design.splitHoldoutNote": "显式划出验证集；不再额外设置交叉验证折。",
    "design.splitCv": "训练集内交叉验证 + 独立测试集",
    "design.splitCvNote": "不单独划验证集；在训练集内部设置 K 折交叉验证。",
    "design.splitTrainOnly": "仅训练集内交叉验证",
    "design.splitTrainOnlyNote": "不划独立测试集，适合先快速探索。",
    "design.cvFoldTitle": "训练集内交叉验证折数",
    "design.cvFoldNote": "这个参数属于数据划分，不属于模型结构参数。",
    "design.targetSource": "监督数值：ppm_mg_kg",
    "design.targetTitle": "训练目标",
    "design.testSet": "独立测试集",
    "design.trainSet": "训练集",
    "design.tri": "三分类风险分层",
    "design.triNote": "由 PPM 范围自动生成。",
    "design.triRule": "低风险 / 中风险 / 高风险自动按范围生成。",
    "design.valSet": "验证集",
    "design.valDisabled": "交叉验证模式下不单独设置验证集。",
    "design.testDisabled": "仅训练集模式下不划独立测试集。",
    "logOrb.button": "日志",
    "logOrb.clear": "清空",
    "logOrb.copy": "复制",
    "logOrb.copied": "已复制",
    "logOrb.empty": "还没有日志。",
    "logOrb.path": "保存路径",
    "logOrb.ready": "未开始记录。",
    "logOrb.recording": "正在记录本次操作和报错。",
    "logOrb.saved": "已保存",
    "logOrb.saveFail": "保存失败",
    "logOrb.start": "开始记录",
    "logOrb.stop": "停止并保存",
    "logOrb.title": "运行日志",
    "workshop.activation": "激活函数",
    "workshop.create": "生成工坊实验项目",
    "workshop.dropout": "Dropout",
    "workshop.ensemble": "Ensemble 融合",
    "workshop.ensembleNote": "比较多个成员平均或投票。",
    "workshop.finetuneMlp": "微调 CNN + MLP",
    "workshop.finetuneMlpNote": "允许 backbone 小学习率微调。",
    "workshop.freezeMlp": "冻结 CNN + MLP",
    "workshop.freezeMlpNote": "提取 CNN embedding，只训练后端 MLP。",
    "workshop.layers": "MLP 层数",
    "workshop.currentPlan": "当前工坊方案",
    "workshop.demoNote": "演示工程已预置：冻结 CNN embedding，后接 MLP 后端进行增强对比。",
    "workshop.note": "基于已有候选模型继续测试后端神经网络，例如冻结 1D-CNN backbone 后接入 MLP。",
    "workshop.openTraining": "打开到模型训练台",
    "workshop.tag": "增强实验",
    "workshop.title": "模型工坊",
    "workshop.width": "隐藏层宽度",
  },
  en: {
    "action.defaults": "Defaults",
    "advanced.paths": "Advanced paths",
    "aggregate.run": "Generate Parameter Comparison",
    "aggregate.title": "Parameter Comparison",
    "app.title": "SpectraMatrix",
    "app.workspace": "Workspace",
    "brand.subtitle": "Local workbench",
    "candidate.select": "Select Best Models",
    "candidate.title": "Candidate Models",
    "console.action": "Action",
    "console.clear": "Clear",
    "console.empty": "Run an action to populate this console.",
    "console.output": "Key output",
    "console.status": "Status",
    "console.time": "Time",
    "console.title": "Debug Log",
    "context.changeData": "Change Data",
    "context.dataset": "Current training data",
    "data.inspectCurrent": "Inspect Current Data",
    "data.subtitle": "Download the templates, prepare two standard CSV files, then drop them here for sample_link_code and PPM checks.",
    "data.title": "Import and Inspect Data",
    "datasetInspect.fail": "Inspect failed",
    "datasetInspect.idle": "After importing two CSV files, the app checks samples, wavelengths, and target columns automatically.",
    "datasetInspect.noConfig": "No dataset is ready yet. Import a spectral matrix and supervision labels first.",
    "datasetInspect.run": "Recheck",
    "datasetInspect.success": "Inspect complete",
    "datasetInspect.tag": "Auto",
    "datasetInspect.title": "Dataset Check Result",
    "datasetCode.confirm": "Use This Dataset",
    "datasetCode.label": "Training data code",
    "datasetCode.locked": "Training data confirmed: ",
    "datasetCode.needCode": "Enter a training data code.",
    "datasetCode.note": "After import checks pass, give this dataset a code. It follows the design, training, selection, workshop, and outputs flow.",
    "datasetCode.ready": "Import check passed. Enter a training data code.",
    "datasetCode.tag": "Required",
    "datasetCode.title": "Confirm Training Data",
    "datasetCode.waiting": "Import the two template CSV files first.",
    "field.aggregateOutput": "Aggregate output",
    "field.candidateOutput": "Candidate output",
    "field.configPath": "Config path",
    "field.direction": "Direction",
    "field.groupBy": "Group by",
    "field.logType": "Log type",
    "field.matrixConfig": "Matrix config",
    "field.matrixOutput": "Matrix output",
    "field.maxTasks": "Tasks this run (blank = all)",
    "field.metric": "Metric",
    "field.outputFolder": "Output folder",
    "field.registryCsv": "Registry CSV",
    "field.registryOutput": "Result table output folder",
    "field.taskFolder": "Task folder",
    "field.top": "Top",
    "factorial.add": "Add Preset Factor",
    "factorial.apply": "Apply Full Factorial",
    "factorial.applied": "Current selections synced; total combinations were refreshed.",
    "factorial.applying": "Syncing current selections...",
    "factorial.count": "Count",
    "factorial.customPlaceholder": "Custom level, e.g. 0.0002 or [16,32,64]",
    "factorial.customSelection": "Custom selection",
    "factorial.draftTotal": "Draft total",
    "factorial.duplicate": "Duplicate factor: ",
    "factorial.exhausted": "All preset factors are already in the table.",
    "factorial.emptyFactor": "Enter a factor name.",
    "factorial.emptyLevels": "Each factor needs at least one optional value.",
    "factorial.factor": "Factor",
    "factorial.fail": "Full factorial design failed",
    "factorial.idle": "Current selections are applied automatically when generating or exporting.",
    "factorial.levelPlaceholder": "Example: relu, gelu or 0.1, 0.2",
    "factorial.levels": "Optional values (selected only)",
    "factorial.levelAdd": "Add Value",
    "factorial.levelParseFail": "Could not parse the custom value. Enter a number, text, or JSON array.",
    "factorial.windowParseFail": "Window format should be 800-1100; stitched windows can be 800-900;1000-1100.",
    "factorial.modeApplied": "Recommended mode loaded. You can generate the training matrix directly.",
    "factorial.note": "Choose factors and optional values from the preset parameter library. The workbench expands all combinations.",
    "factorial.preset": "Preset group",
    "factorial.remove": "Remove",
    "factorial.title": "Model Optional Values",
    "import.choose": "Choose Files",
    "import.chooseSpectra": "Choose Spectra",
    "import.chooseSupervision": "Choose Labels",
    "import.demoDataset": "Import Demo Dataset",
    "import.empty": "No files imported yet.",
    "import.help": "Recommended: import a CSV package with a wide spectral table plus a supervision table. NPZ is supported; JSON is an auto-generated advanced config.",
    "import.notSelected": "No file selected",
    "import.downloadSpectraTemplate": "Download Spectra Template",
    "import.downloadSupervisionTemplate": "Download Supervision Template",
    "import.readyPair": "Both files are ready to import.",
    "import.spectraHelp": "Drop a wide spectral CSV, or an existing spectral NPZ matrix.",
    "import.spectraTitle": "Spectral Matrix",
    "import.start": "Import and Inspect",
    "import.supervisionHelp": "Drop the numeric supervision CSV, typically sample_link_code plus ppm_mg_kg.",
    "import.supervisionTitle": "Supervision Labels",
    "import.title": "Drop files here",
    "import.waitingPair": "Choose both the spectral matrix and supervision label files.",
    "matrix.create": "Generate Training Matrix",
    "matrix.createdDetail": "The training project was written locally and can be opened in Model Training Desk.",
    "matrix.createdTitle": "Training project generated",
    "matrix.export": "Export Training Matrix Package",
    "matrix.exportedTitle": "Training matrix package exported",
    "matrix.fixedEmpty": "No fixed parameters",
    "matrix.fixedOnly": "No adjustable parameters: one fixed task",
    "matrix.fixedTitle": "Fixed parameters",
    "matrix.gridEmpty": "This matrix has no adjustable parameters and will create one fixed task.",
    "matrix.gridTitle": "Adjustable parameter candidates",
    "matrix.idle": "No training project generated yet.",
    "matrix.limit": "Safety limit (optional)",
    "matrix.limitHelp": "This is not the planned model count. If it is below the total combinations, creation is blocked to avoid accidental oversized matrices.",
    "matrix.limitPlaceholder": "Blank: create all combinations",
    "matrix.limitTooLow": "Safety limit is below the total combinations, so creation was blocked. Clear it or set it to at least the total.",
    "matrix.nextMonitor": "Refresh Task Blocks",
    "matrix.nextQueue": "Open in Training Desk",
    "matrix.note": "Set training environment, target tasks, data split, and optional model values here, then generate a runnable training project.",
    "matrix.presetAll": "No limit",
    "matrix.presetSafety": "Safety limit 10",
    "matrix.presetTotal": "Use total count",
    "matrix.previewFail": "Matrix preview failed",
    "matrix.previewIdle": "Reading parameter matrix...",
    "matrix.previewLoading": "Reading parameter matrix...",
    "matrix.previewReady": "Current matrix total",
    "matrix.previewTaskDetails": "Task details",
    "matrix.running": "Generating the training matrix from current selections...",
    "matrix.step1": "1. Choose Optional Values",
    "matrix.step1Note": "Set candidate values per parameter",
    "matrix.step2": "2. Expand Grid",
    "matrix.step2Note": "Cartesian product of candidates",
    "matrix.step3": "3. Write Tasks",
    "matrix.step3Note": "One runnable task per combination",
    "matrix.tag": "Training Project",
    "matrix.taskUnit": "training tasks",
    "matrix.title": "Model Training Design",
    "matrix.totalLabel": "Total combinations",
    "metric.samples": "Samples",
    "metric.targets": "Targets",
    "metric.wavelengths": "Wavelengths",
    "metric.windows": "Windows",
    "monitor.empty": "Refresh a task folder to inspect queue state.",
    "monitor.refresh": "Refresh Tasks",
    "monitor.selectTask": "Select a task row to view logs.",
    "monitor.title": "Task Progress",
    "nav.data": "Data Import",
    "nav.matrix": "Model Training Design",
    "nav.outputs": "Model Outputs",
    "nav.queue": "Model Training Desk",
    "nav.results": "Result Selection",
    "nav.workshop": "Model Workshop",
    "outputs.note": "Show the current model outputs. Regression tasks use predicted vs measured plots, R2, RMSE, MAE, and residuals. Classification tasks use confusion matrices and per-class metrics.",
    "outputs.modelPicker": "Choose model to display",
    "outputs.regressionPlot": "Predicted vs Measured",
    "outputs.tag": "Charts and Reports",
    "outputs.title": "Model Outputs",
    "project.autoSaveReady": "After opening or saving a project, autosave writes to that project file.",
    "project.advancedPath": "Advanced path",
    "project.choose": "Open",
    "project.dropHint": "Drop .spectramatrix.json to restore data, design, queue, and results.",
    "project.dropTitle": "Open or Resume",
    "project.file": "Project file path",
    "project.noFile": "No project selected",
    "project.open": "Open Project",
    "project.openByPath": "Open by Path",
    "project.openDemo": "Import Demo Data",
    "project.opened": "Project opened and progress restored.",
    "project.save": "Save",
    "project.saveAs": "Save As",
    "project.saveAsSaved": "Project saved as.",
    "project.saveDialogCancel": "Cancel",
    "project.saveDialogConfirm": "Save",
    "project.saveDialogHint": "Enter a readable project file name. It will be saved as .spectramatrix.json.",
    "project.saveDialogName": "Project file name",
    "project.saveDialogTitle": "Save Project File",
    "project.saveDialogTitleAs": "Save As New Project",
    "project.saveNeedName": "Enter a project file name.",
    "project.saved": "Project saved.",
    "project.sidebarTitle": "Workspace Project",
    "queue.dryRun": "Check scripts only, do not train",
    "queue.note": "When the current project contains training tasks, run, pause, rerun failures, and watch progress blocks here.",
    "queue.rerunFailed": "Rerun failed",
    "queue.resume": "Resume Training",
    "queue.run": "Start Training",
    "queue.stop": "Stop Current Run",
    "queue.tag": "Training Project",
    "queue.title": "Model Training Desk",
    "results.advancedRule": "Advanced: manual metric and output paths",
    "results.aggregateNote": "Use this when you want to compare parameter families, such as spectral windows, model structures, or preprocessing methods.",
    "results.currentProject": "Current Project",
    "results.finalCandidate": "Set as Final Candidate",
    "results.keepHowMany": "Keep top models",
    "results.metricBalancedAccuracy": "Classification balanced accuracy, higher is better",
    "results.metricMae": "Mean absolute error, lower is better",
    "results.metricRmse": "Regression error, lower is better",
    "results.optional": "Optional",
    "results.readyState": "Selection state",
    "results.resultTable": "Result table",
    "results.stepRule": "2. Choose selection rule",
    "results.stepRuleNote": "Regression usually uses RMSE or MAE, where lower is better. Classification usually uses balanced accuracy, where higher is better.",
    "results.stepSource": "1. Read training results",
    "results.stepSourceNote": "Use the current project's task folder and result table first. Most users do not need to enter paths.",
    "results.subtitle": "After training, read the current results here and pick the model combinations worth validating.",
    "results.title": "Result Selection",
    "results.trainingTasks": "Training tasks",
    "results.useCurrent": "Use Current Results",
    "scan.run": "Scan Training Results",
    "scan.title": "Scan Runs",
    "table.activation": "Activation",
    "table.fold": "Fold",
    "table.log": "Log",
    "table.metric": "Metric",
    "table.model": "Model",
    "table.status": "Status",
    "table.task": "Task",
    "table.window": "Window",
    "design.binary": "Binary screening",
    "design.binaryNote": "Derived automatically from a PPM threshold.",
    "design.binaryRule": "Below: ppm < threshold; above: ppm ≥ threshold",
    "design.binaryThreshold": "Binary threshold",
    "design.device": "Device",
    "design.envCheck": "Check Environment",
    "design.envTitle": "Training Environment",
    "design.exportTarget": "Export target",
    "design.framework": "Framework",
    "design.lowMax": "Low-risk max",
    "design.midMax": "Medium-risk max",
    "design.precision": "Precision",
    "design.ratio": "Ratio",
    "design.regression": "PPM regression",
    "design.regressionNote": "Predict continuous PPM directly.",
    "design.ruleTitle": "Classification Criteria",
    "design.ruleEmpty": "Regression only. No classification thresholds are needed.",
    "design.splitNote": "Split by sample_link_code groups to avoid sample leakage.",
    "design.splitTitle": "Data Split",
    "design.splitHoldout": "Train + validation + independent test",
    "design.splitHoldoutNote": "Use an explicit validation set; no extra CV-fold setting.",
    "design.splitCv": "CV inside training + independent test",
    "design.splitCvNote": "No standalone validation set; choose K-fold CV inside training.",
    "design.splitTrainOnly": "Training-set CV only",
    "design.splitTrainOnlyNote": "No independent test split; useful for quick exploration.",
    "design.cvFoldTitle": "Training-set CV folds",
    "design.cvFoldNote": "This belongs to data splitting, not model architecture.",
    "design.targetSource": "Supervision value: ppm_mg_kg",
    "design.targetTitle": "Training Targets",
    "design.testSet": "Independent test",
    "design.trainSet": "Training set",
    "design.tri": "Three-class risk",
    "design.triNote": "Derived automatically from PPM ranges.",
    "design.triRule": "Low / medium / high risk are generated by ranges.",
    "design.valSet": "Validation set",
    "design.valDisabled": "No standalone validation set in CV mode.",
    "design.testDisabled": "No independent test split in training-only mode.",
    "logOrb.button": "Log",
    "logOrb.clear": "Clear",
    "logOrb.copy": "Copy",
    "logOrb.copied": "Copied",
    "logOrb.empty": "No logs yet.",
    "logOrb.path": "Save path",
    "logOrb.ready": "Not recording.",
    "logOrb.recording": "Recording this session.",
    "logOrb.saved": "Saved",
    "logOrb.saveFail": "Save failed",
    "logOrb.start": "Start",
    "logOrb.stop": "Stop & save",
    "logOrb.title": "Run Log",
    "workshop.activation": "Activation",
    "workshop.create": "Generate Workshop Project",
    "workshop.dropout": "Dropout",
    "workshop.ensemble": "Ensemble Fusion",
    "workshop.ensembleNote": "Compare averaging or voting across members.",
    "workshop.finetuneMlp": "Fine-tune CNN + MLP",
    "workshop.finetuneMlpNote": "Allow low-LR backbone fine-tuning.",
    "workshop.freezeMlp": "Frozen CNN + MLP",
    "workshop.freezeMlpNote": "Extract CNN embeddings and train only the MLP backend.",
    "workshop.layers": "MLP layers",
    "workshop.currentPlan": "Current workshop plan",
    "workshop.demoNote": "Demo project preset: freeze CNN embeddings, then compare an MLP backend.",
    "workshop.note": "Test backend neural networks from existing candidates, such as frozen 1D-CNN backbone plus MLP.",
    "workshop.openTraining": "Open in Training Desk",
    "workshop.tag": "Enhancement",
    "workshop.title": "Model Workshop",
    "workshop.width": "Hidden width",
  },
};

document.querySelector("#refresh-defaults").addEventListener("click", loadDefaults);
document.querySelector("#clear-results").addEventListener("click", () => {
  resultRows.innerHTML = `<tr class="empty-row"><td colspan="4">${t("console.empty")}</td></tr>`;
  jsonOutput.textContent = "{}";
  resultSummary.textContent = currentLanguage === "zh" ? "尚未运行" : "No action yet";
});
document.querySelector("#inspect-current").addEventListener("click", () => forms.dataset.requestSubmit());
datasetConfirm.addEventListener("click", confirmActiveDataset);
datasetCodeInput.addEventListener("input", () => updateDatasetConfirmState());
languageToggle.addEventListener("click", () => {
  currentLanguage = currentLanguage === "zh" ? "en" : "zh";
  localStorage.setItem("spectral_workbench_language", currentLanguage);
  applyLanguage();
});

for (const button of document.querySelectorAll("[data-view-target]")) {
  button.addEventListener("click", () => setActiveView(button.dataset.viewTarget));
}
for (const button of document.querySelectorAll("[data-view-jump]")) {
  button.addEventListener("click", () => setActiveView(button.dataset.viewJump));
}
for (const toggle of targetToggles) {
  toggle.addEventListener("change", () => {
    updateTargetRuleVisibility();
    factorialTouched = true;
    updateFactorialDraftTotal();
    persistTrainingDesignDraft();
    recordDiagnosticEvent("target.changed", targetSelectionSnapshot());
  });
}
for (const input of splitModeInputs) {
  input.addEventListener("change", () => {
    updateSplitModeUi();
    factorialTouched = true;
    updateFactorialDraftTotal();
    persistTrainingDesignDraft();
    recordDiagnosticEvent("split.changed", splitSelectionSnapshot());
  });
}
if (cvFoldOptions) {
  cvFoldOptions.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-cv-fold]");
    if (!button) {
      return;
    }
    button.classList.toggle("active");
    button.setAttribute("aria-pressed", button.classList.contains("active") ? "true" : "false");
    if (!selectedCvFolds().length) {
      button.classList.add("active");
      button.setAttribute("aria-pressed", "true");
    }
    factorialTouched = true;
    updateFactorialDraftTotal();
    persistTrainingDesignDraft();
    recordDiagnosticEvent("cv_fold.changed", { folds: selectedCvFolds() });
  });
}
for (const control of [
  trainingFramework,
  trainingDevice,
  trainingPrecision,
  trainingExportTarget,
  binaryThreshold,
  triLowMax,
  triMidMax,
  splitTrainRatio,
  splitValRatio,
  splitTestRatio,
  workshopMlpLayers,
  workshopHiddenWidth,
  workshopActivation,
  workshopDropout,
].filter(Boolean)) {
  control.addEventListener("input", () => persistTrainingDesignDraft());
  control.addEventListener("change", () => {
    updateSplitModeUi();
    updateFactorialDraftTotal();
    renderWorkshopPlan();
    persistTrainingDesignDraft();
  });
}
if (logOrbToggle) {
  logOrbToggle.addEventListener("click", () => {
    const open = logOrbPanel.hidden;
    logOrbPanel.hidden = !open;
    logOrbToggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
}
if (logOrbCopy) {
  logOrbCopy.addEventListener("click", async () => {
    await navigator.clipboard.writeText(diagnosticsEvents.map((event) => JSON.stringify(event)).join("\n"));
    logOrbCopy.querySelector("span").textContent = t("logOrb.copied");
    window.setTimeout(() => {
      logOrbCopy.querySelector("span").textContent = t("logOrb.copy");
    }, 1200);
  });
}
if (logOrbClear) {
  logOrbClear.addEventListener("click", () => {
    diagnosticsEvents = [];
    persistDiagnosticsEvents();
    renderDiagnosticsEvents();
  });
}
if (logRecorderStart) {
  logRecorderStart.addEventListener("click", () => {
    startDiagnosticsRecording();
  });
}
if (logRecorderStop) {
  logRecorderStop.addEventListener("click", () => {
    stopAndSaveDiagnosticsRecording();
  });
}

forms.dataset.addEventListener("submit", (event) => {
  event.preventDefault();
  inspectDataset({ manual: true });
});

forms.matrix.addEventListener("submit", (event) => {
  event.preventDefault();
  createMatrix();
});

forms.queue.addEventListener("submit", (event) => {
  event.preventDefault();
  const payload = formPayload(forms.queue);
  payload.max_tasks = optionalNumber(payload.max_tasks);
  payload.dry_run = forms.queue.elements.dry_run.checked;
  payload.rerun_failed = forms.queue.elements.rerun_failed.checked;
  startQueueJob(payload);
});

if (queueResumeButton) {
  queueResumeButton.addEventListener("click", () => {
    const payload = formPayload(forms.queue);
    payload.max_tasks = optionalNumber(payload.max_tasks);
    payload.dry_run = forms.queue.elements.dry_run.checked;
    payload.rerun_failed = forms.queue.elements.rerun_failed.checked;
    startQueueJob(payload);
  });
}

if (queueStopButton) {
  queueStopButton.addEventListener("click", () => stopQueueJob());
}
if (projectSaveButton) {
  projectSaveButton.addEventListener("click", () => handleProjectSaveClick());
}
if (projectSaveAsButton) {
  projectSaveAsButton.addEventListener("click", () => openProjectSaveDialog({ saveAs: true }));
}
if (projectSaveConfirm) {
  projectSaveConfirm.addEventListener("click", () => confirmProjectSaveDialog());
}
if (projectSaveCancel) {
  projectSaveCancel.addEventListener("click", () => closeProjectSaveDialog());
}
if (projectSaveDialog) {
  projectSaveDialog.addEventListener("cancel", () => closeProjectSaveDialog());
}
if (projectSaveNameInput) {
  projectSaveNameInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      confirmProjectSaveDialog();
    }
  });
}
if (projectBrowseButton && projectFileInput) {
  projectBrowseButton.addEventListener("click", () => projectFileInput.click());
}
if (projectOpenDemoButton) {
  projectOpenDemoButton.addEventListener("click", () => openDemoProject());
}
if (resultsUseCurrent) {
  resultsUseCurrent.addEventListener("click", () => useCurrentTrainingResults());
}
for (const button of metricChoices) {
  button.addEventListener("click", () => {
    setResultMetricChoice(button.dataset.metricChoice || "", button.dataset.directionChoice || "auto");
  });
}
for (const button of topChoices) {
  button.addEventListener("click", () => {
    setResultTopChoice(button.dataset.topChoice || "5");
  });
}
if (projectDropzone && projectFileInput) {
  projectDropzone.addEventListener("click", () => projectFileInput.click());
  projectDropzone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      projectFileInput.click();
    }
  });
  for (const eventName of ["dragenter", "dragover"]) {
    projectDropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      projectDropzone.classList.add("dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    projectDropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      projectDropzone.classList.remove("dragging");
    });
  }
  projectDropzone.addEventListener("drop", (event) => {
    openProjectFromFile(event.dataTransfer.files && event.dataTransfer.files[0]);
  });
}
if (projectFileInput) {
  projectFileInput.addEventListener("change", () => {
    openProjectFromFile(projectFileInput.files && projectFileInput.files[0]);
    projectFileInput.value = "";
  });
}
if (projectOpenButton) {
  projectOpenButton.addEventListener("click", () => openProjectFile());
}
if (projectFilePath) {
  projectFilePath.addEventListener("change", () => {
    saveWorkspaceState({
      projectPath: projectFilePath.value.trim(),
      projectAutosaveEnabled: Boolean(projectFilePath.value.trim()),
    });
  });
}

forms.monitor.addEventListener("submit", (event) => {
  event.preventDefault();
  refreshTasks();
});

forms.scan.addEventListener("submit", (event) => {
  event.preventDefault();
  useCurrentTrainingResults({ silent: true });
  postAction("Run scan", "/api/runs/scan", formPayload(forms.scan), (data) => {
    if (data.registry) {
      forms.candidate.elements.registry.value = data.registry;
      forms.aggregate.elements.registry.value = data.registry;
      forms.candidate.elements.metric.value = "";
      forms.aggregate.elements.metric.value = "";
      saveWorkspaceState({ registry: data.registry, tasksDir: forms.scan.elements.runs.value });
      renderResultSelectionState();
      renderModelOutputsFromRegistry(data.registry, { silent: true });
    }
  });
});

forms.candidate.addEventListener("submit", (event) => {
  event.preventDefault();
  useCurrentTrainingResults({ silent: true });
  const payload = formPayload(forms.candidate);
  if (!payload.registry) {
    appendResult(
      "Candidate select",
      "fail",
      currentLanguage === "zh" ? "请先扫描当前训练结果。" : "Scan the current training results first.",
      { error: "missing registry" },
    );
    renderResultSelectionState();
    return;
  }
  payload.metric = payload.metric || null;
  payload.top = Number(payload.top || 10);
  postAction("Candidate select", "/api/candidates/select", payload, (data) => {
    saveWorkspaceState({ registry: payload.registry, candidates: data.candidates || "", candidateReport: data.report || "" });
    renderResultSelectionState();
    renderModelOutputsFromRegistry(payload.registry);
  });
});

forms.aggregate.addEventListener("submit", (event) => {
  event.preventDefault();
  useCurrentTrainingResults({ silent: true });
  const payload = formPayload(forms.aggregate);
  if (!payload.registry) {
    appendResult(
      "Matrix aggregate",
      "fail",
      currentLanguage === "zh" ? "请先扫描当前训练结果。" : "Scan the current training results first.",
      { error: "missing registry" },
    );
    renderResultSelectionState();
    return;
  }
  payload.metric = payload.metric || null;
  payload.group_by = String(payload.group_by || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  postAction("Matrix aggregate", "/api/matrix/aggregate", payload, (data) => {
    saveWorkspaceState({ registry: payload.registry, aggregateReport: data.report || "", aggregateSummary: data.group_summary || "" });
    renderModelOutputsFromRegistry(payload.registry);
  });
});

taskRows.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-task-dir]");
  if (!button) {
    return;
  }
  loadTaskLog(button.dataset.taskDir);
});
if (taskBlocks) {
  taskBlocks.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-task-dir]");
    if (!button) {
      return;
    }
    loadTaskLog(button.dataset.taskDir);
  });
}
if (matrixCreatedTaskBlocks) {
  matrixCreatedTaskBlocks.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-task-dir]");
    if (!button) {
      return;
    }
    loadTaskLog(button.dataset.taskDir);
    setActiveView("queue");
  });
}
if (outputModelPicker) {
  outputModelPicker.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-output-task-id]");
    if (!button) {
      return;
    }
    selectedOutputTaskId = button.dataset.outputTaskId || "";
    renderModelOutputsFromRegistry(workspaceState.registry || forms.candidate.elements.registry.value || "", {
      taskId: selectedOutputTaskId,
    });
  });
}

taskLogKind.addEventListener("change", () => {
  const taskDir = taskLogKind.dataset.taskDir;
  if (taskDir) {
    loadTaskLog(taskDir);
  }
});

bindImportSlot("spectra", spectraDropzone, spectraFileInput, spectraBrowse, spectraSelected);
bindImportSlot("supervision", supervisionDropzone, supervisionFileInput, supervisionBrowse, supervisionSelected);
if (importDemoDataset) {
  importDemoDataset.addEventListener("click", () => importDemoDatasetPackage());
}
importStart.addEventListener("click", () => importSelectedPair());
for (const button of document.querySelectorAll("[data-matrix-limit]")) {
  button.addEventListener("click", () => {
    const value = button.dataset.matrixLimit || "";
    forms.matrix.elements.max_tasks.value = value === "total" && currentMatrixPreview
      ? currentMatrixPreview.total_combinations
      : value;
  });
}
factorialAdd.addEventListener("click", () => {
  factorialTouched = true;
  factorialModeList.dataset.activeMode = "";
  renderFactorialModes();
  const next = nextAvailableFactor();
  if (!next) {
    setFactorialStatus(t("factorial.exhausted"), "warn");
    return;
  }
  addFactorRow(next.key, next.presets[0].id);
  refreshFactorOptions();
  updateFactorialDraftTotal();
  persistTrainingDesignDraft();
});
if (factorialReset) {
  factorialReset.addEventListener("click", () => {
    syncFactorialEditor(currentMatrixPreview, { force: true });
    setFactorialStatus(t("factorial.idle"), "");
    persistTrainingDesignDraft();
  });
}
if (factorialApply) {
  factorialApply.addEventListener("click", () => applyFullFactorialDesign());
}
matrixExport.addEventListener("click", () => createMatrix({ exportOnly: true }));
factorialModeList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-factorial-mode]");
  if (!button) {
    return;
  }
  applyFactorialMode(button.dataset.factorialMode);
  persistTrainingDesignDraft();
});
factorialRows.addEventListener("change", (event) => {
  factorialTouched = true;
  factorialModeList.dataset.activeMode = "";
  renderFactorialModes();
  const row = event.target.closest(".factorial-row");
  if (row && event.target.matches("[data-factor-key]")) {
    const factor = factorByKey(event.target.value);
    const presetSelect = row.querySelector("[data-factor-preset]");
    const presetId = factor ? factor.presets[0].id : "";
    row.dataset.currentValues = "[]";
    updateCustomLevelPlaceholder(row);
    renderPresetOptions(presetSelect, factor, presetId);
    renderLevelCards(row, selectedValuesForPreset(factor, presetId));
  }
  if (row && event.target.matches("[data-factor-preset]")) {
    const factor = factorByKey(row.querySelector("[data-factor-key]").value);
    renderLevelCards(row, selectedValuesForPreset(factor, event.target.value, readCurrentValues(row)));
  }
  refreshFactorOptions();
  updateFactorialDraftTotal();
  persistTrainingDesignDraft();
});
factorialRows.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-factor-remove]");
  const levelButton = event.target.closest("button[data-level-card]");
  const addLevelButton = event.target.closest("button[data-level-add]");
  if (levelButton) {
    factorialTouched = true;
    factorialModeList.dataset.activeMode = "";
    renderFactorialModes();
    toggleLevelCard(levelButton);
    markRowAsCustom(levelButton.closest(".factorial-row"));
    updateFactorialDraftTotal();
    persistTrainingDesignDraft();
    return;
  }
  if (addLevelButton) {
    factorialTouched = true;
    factorialModeList.dataset.activeMode = "";
    renderFactorialModes();
    addCustomLevel(addLevelButton.closest(".factorial-row"));
    updateFactorialDraftTotal();
    persistTrainingDesignDraft();
    return;
  }
  if (!button) {
    return;
  }
  factorialTouched = true;
  factorialModeList.dataset.activeMode = "";
  renderFactorialModes();
  button.closest(".factorial-row").remove();
  if (!factorialRows.querySelector(".factorial-row")) {
    const next = nextAvailableFactor() || visibleFactorCatalog()[0];
    addFactorRow(next.key, next.presets[0].id, next.presets[0].values);
  }
  refreshFactorOptions();
  updateFactorialDraftTotal();
  persistTrainingDesignDraft();
});
factorialRows.addEventListener("keydown", (event) => {
  if (!event.target.matches("[data-level-custom]") || event.key !== "Enter") {
    return;
  }
  event.preventDefault();
  factorialTouched = true;
  factorialModeList.dataset.activeMode = "";
  renderFactorialModes();
  addCustomLevel(event.target.closest(".factorial-row"));
  updateFactorialDraftTotal();
  persistTrainingDesignDraft();
});
matrixGoQueue.addEventListener("click", () => {
  setActiveView("queue");
  refreshTasks({ silent: true });
});
matrixGoMonitor.addEventListener("click", () => {
  setActiveView("queue");
  refreshTasks({ silent: true });
});

async function loadDefaults() {
  setApiState(currentLanguage === "zh" ? "检查 API" : "Checking API", "");
  try {
    const health = await fetchJson("/health");
    if (health.status !== "ok") {
      throw new Error("Unexpected health response");
    }
    const defaults = await fetchJson("/api/workbench/defaults");
    setDefaults(defaults);
    await restoreWorkspaceState();
    await openInitialProjectFromUrl();
    await previewMatrix({ silent: true });
    renderResultSelectionState();
    setApiState(currentLanguage === "zh" ? "API 就绪" : "API ready", "ok");
  } catch (error) {
    setApiState(currentLanguage === "zh" ? "API 不可用" : "API unavailable", "fail");
    appendResult("Defaults", "fail", error.message, { error: error.message });
  }
}

async function openInitialProjectFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const projectPath = params.get("project");
  if (!projectPath || !projectFilePath) {
    return;
  }
  projectFilePath.value = projectPath;
  await openProjectFile();
}

async function postAction(label, path, payload, onSuccess) {
  const submitter = document.activeElement;
  if (submitter instanceof HTMLButtonElement) {
    submitter.disabled = true;
  }
  try {
    const data = await fetchJson(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    appendResult(label, "ok", summarizeOutput(data), data);
    if (onSuccess) {
      onSuccess(data);
    }
  } catch (error) {
    appendResult(label, "fail", error.message, { error: error.message, payload });
  } finally {
    if (submitter instanceof HTMLButtonElement) {
      submitter.disabled = false;
    }
  }
}

function bindImportSlot(slot, dropzone, input, browse, selectedLabel) {
  browse.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    selectImportFile(slot, input.files && input.files[0], selectedLabel);
    input.value = "";
  });
  for (const eventName of ["dragenter", "dragover"]) {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.add("dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.remove("dragging");
    });
  }
  dropzone.addEventListener("drop", (event) => {
    selectImportFile(slot, event.dataTransfer.files && event.dataTransfer.files[0], selectedLabel);
  });
}

function selectImportFile(slot, file, selectedLabel) {
  if (!file) {
    return;
  }
  selectedImportFiles[slot] = file;
  selectedLabel.removeAttribute("data-i18n");
  selectedLabel.textContent = `${file.name} · ${formatBytes(file.size)}`;
  updateImportPairState();
}

function updateImportPairState() {
  const ready = Boolean(selectedImportFiles.spectra && selectedImportFiles.supervision);
  importStart.disabled = !ready;
  importSelectionStatus.textContent = ready ? t("import.readyPair") : t("import.waitingPair");
}

async function importSelectedPair() {
  if (!selectedImportFiles.spectra || !selectedImportFiles.supervision) {
    updateImportPairState();
    return;
  }
  await importFiles([selectedImportFiles.spectra, selectedImportFiles.supervision]);
}

async function importFiles(files) {
  if (files.length === 0) {
    return;
  }
  importSummary.innerHTML = `<p>${currentLanguage === "zh" ? "正在导入..." : "Importing..."}</p>`;
  try {
    const payload = { files: [] };
    for (const file of files) {
      payload.files.push({
        name: file.name,
        content_base64: await fileToBase64(file),
        size: file.size,
        mime_type: file.type || "application/octet-stream",
      });
    }
    const data = await fetchJson("/api/dataset/import-files", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderImportSummary(data);
    if (data.dataset_config) {
      forms.dataset.elements.config.value = data.dataset_config;
      saveWorkspaceState({ datasetConfig: data.dataset_config, importManifest: data.import_dir || "" });
      await inspectDataset({ manual: false });
    }
    appendResult("Dataset import", "ok", summarizeImport(data), data);
  } catch (error) {
    importSummary.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
    appendResult("Dataset import", "fail", error.message, { error: error.message });
  } finally {
    spectraFileInput.value = "";
    supervisionFileInput.value = "";
  }
}

async function importDemoDatasetPackage() {
  if (!importDemoDataset) {
    return;
  }
  importDemoDataset.disabled = true;
  importSummary.innerHTML = `<p>${currentLanguage === "zh" ? "正在导入演示数据集..." : "Importing demo dataset..."}</p>`;
  try {
    const data = await fetchJson("/api/demo/import", { method: "POST" });
    renderImportSummary(data);
    if (data.dataset_config) {
      forms.dataset.elements.config.value = data.dataset_config;
      saveWorkspaceState({ datasetConfig: data.dataset_config, importManifest: data.import_dir || "" });
      await inspectDataset({ manual: false });
    }
    appendResult("Demo dataset import", "ok", summarizeImport(data), data);
  } catch (error) {
    importSummary.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
    appendResult("Demo dataset import", "fail", error.message, { error: error.message });
  } finally {
    importDemoDataset.disabled = false;
  }
}

async function inspectDataset(options = {}) {
  const payload = formPayload(forms.dataset);
  if (!payload.config) {
    setDatasetCheckMessage(t("datasetInspect.noConfig"), "warn");
    return;
  }
  setDatasetCheckMessage(currentLanguage === "zh" ? "正在检查数据..." : "Inspecting dataset...", "pending");
  try {
    const data = await fetchJson("/api/dataset/inspect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    updateDatasetCards(data);
    const message = `${t("datasetInspect.success")}：${data.samples} ${t("metric.samples")}，${data.wavelengths} ${t("metric.wavelengths")}，${targetCount(data.target_columns)} ${t("metric.targets")}`;
    setDatasetCheckMessage(message, "ok");
    appendResult(options.manual ? "Dataset recheck" : "Dataset inspect", "ok", summarizeOutput(data), data);
  } catch (error) {
    setDatasetCheckMessage(`${t("datasetInspect.fail")}：${error.message}`, "fail");
    appendResult("Dataset inspect", "fail", error.message, { error: error.message, payload });
  }
}

function setDatasetCheckMessage(text, state) {
  datasetCheckMessage.textContent = text;
  datasetCheckMessage.className = `check-message ${state || ""}`.trim();
}

async function createMatrix(options = {}) {
  const submitter = document.activeElement;
  if (submitter instanceof HTMLButtonElement) {
    submitter.disabled = true;
  }
  const payload = formPayload(forms.matrix);
  payload.max_tasks = optionalNumber(payload.max_tasks);
  matrixResult.hidden = true;
  setMatrixStatus(t("matrix.running"), "pending");
  const designData = await applyFullFactorialDesign({ silent: true, updateMatrixStatus: false });
  if (!designData) {
    setMatrixStatus(currentLanguage === "zh"
      ? "无法按当前选择生成训练矩阵，请检查模型可选参数。"
      : "Could not generate the training matrix from the current selections. Check the optional model values.",
      "fail");
    if (submitter instanceof HTMLButtonElement) {
      submitter.disabled = false;
    }
    return;
  }
  payload.config = designData.config;
  payload.out = uniqueMatrixOutputPath(payload.out);
  let preview = designData.preview || currentMatrixPreview;
  if (!preview) {
    preview = await previewMatrix({ silent: true });
  }
  if (!preview) {
    if (submitter instanceof HTMLButtonElement) {
      submitter.disabled = false;
    }
    return;
  }
  if (preview && payload.max_tasks !== null && payload.max_tasks < preview.total_combinations) {
    setMatrixStatus(`${t("matrix.limitTooLow")} ${preview.total_combinations} ${t("matrix.taskUnit")}`, "warn");
    if (submitter instanceof HTMLButtonElement) {
      submitter.disabled = false;
    }
    return;
  }
  setMatrixStatus(t("matrix.running"), "pending");
  try {
    const data = await fetchJson("/api/matrix/create-npz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    appendResult("Matrix create", "ok", summarizeOutput(data), data);
    await handleMatrixCreated(data, options);
  } catch (error) {
    setMatrixStatus(error.message, "fail");
    appendResult("Matrix create", "fail", error.message, { error: error.message, payload });
  } finally {
    if (submitter instanceof HTMLButtonElement) {
      submitter.disabled = false;
    }
  }
}

function uniqueMatrixOutputPath(basePath) {
  const source = String(basePath || "").trim();
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\..*$/, "").replace("T", "-");
  return source ? `${source}_${stamp}` : `spectramatrix_training_project_${stamp}`;
}

function setMatrixStatus(text, state) {
  matrixStatus.removeAttribute("data-i18n");
  matrixStatus.textContent = text;
  matrixStatus.className = `check-message ${state || ""}`.trim();
}

async function previewMatrix(options = {}) {
  const payload = formPayload(forms.matrix);
  if (!payload.config) {
    renderMatrixPreview(null);
    return null;
  }
  if (!options.silent) {
    setMatrixStatus(t("matrix.previewLoading"), "pending");
  }
  try {
    const data = await fetchJson("/api/matrix/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: payload.config }),
    });
    currentMatrixPreview = data;
    renderMatrixPreview(data);
    if (!options.keepStatus) {
      setMatrixStatus(`${t("matrix.previewReady")}：${data.total_combinations} ${t("matrix.taskUnit")}`, "ok");
    }
    if (!options.silent) {
      appendResult("Matrix preview", "ok", `combinations=${data.total_combinations}, ${displayFormula(data.formula)}`, data);
    }
    return data;
  } catch (error) {
    currentMatrixPreview = null;
    renderMatrixPreview(null);
    setMatrixStatus(`${t("matrix.previewFail")}：${error.message}`, "fail");
    if (!options.silent) {
      appendResult("Matrix preview", "fail", error.message, { error: error.message, payload });
    }
    return null;
  }
}

function renderMatrixPreview(data) {
  if (!data) {
    matrixTotal.textContent = "--";
    matrixFormula.textContent = t("matrix.previewIdle");
    matrixGridList.innerHTML = `<p class="empty-hint">${t("matrix.gridEmpty")}</p>`;
    matrixFixedList.innerHTML = `<p class="empty-hint">${t("matrix.fixedEmpty")}</p>`;
    syncFactorialEditor(null);
    return;
  }

  matrixTotal.textContent = data.total_combinations ?? "--";
  matrixFormula.textContent = displayFormula(data.formula);
  const overrideRows = Object.entries(data.task_specific_overrides || {}).flatMap(([taskName, rows]) =>
    (rows || []).map((row) => ({ ...row, key: `${taskName}.${row.key}` })),
  );
  const gridRows = [...(data.grid || []), ...overrideRows];
  matrixGridList.innerHTML = gridRows.length
    ? gridRows.map(renderGridParamRow).join("")
    : `<p class="empty-hint">${t("matrix.gridEmpty")}</p>`;

  const fixedEntries = Object.entries(data.fixed || {});
  matrixFixedList.innerHTML = fixedEntries.length
    ? fixedEntries.map(renderFixedParamChip).join("")
    : `<p class="empty-hint">${t("matrix.fixedEmpty")}</p>`;
  syncFactorialEditor(data);
}

function renderGridParamRow(row) {
  return `
    <div class="grid-param-row">
      <div>
        <strong>${escapeHtml(displayParamKey(row.key))}</strong>
        <small>${escapeHtml(displayParamValues(row.key, row.values || []))}</small>
      </div>
      <span>×${escapeHtml(row.count ?? 1)}</span>
    </div>
  `;
}

function syncFactorialEditor(data, options = {}) {
  if (!factorialRows || (!options.force && factorialTouched)) {
    return;
  }
  const rows = data && Array.isArray(data.grid) ? data.grid.filter((row) => row.key !== "cv_fold") : [];
  if (rows.length) {
    renderFactorialRows(rows.map((row) => factorRowDefinition(row.key, row.values || [])));
  } else {
    renderFactorialRows([]);
  }
  factorialTouched = false;
  factorialModeList.dataset.activeMode = "";
  renderFactorialModes();
  updateFactorialDraftTotal();
}

function renderFactorialRows(definitions) {
  factorialRows.innerHTML = "";
  for (const definition of definitions) {
    addFactorRow(definition.key, definition.preset, definition.values);
  }
  refreshFactorOptions();
  updateFactorialDraftTotal();
}

function addFactorRow(key, presetId, currentValues = []) {
  const factor = (key === "cv_fold" ? null : factorByKey(key)) || visibleFactorCatalog()[0];
  const selectedPreset = presetId || factor.presets[0].id;
  const initialValues = currentValues && currentValues.length
    ? currentValues
    : selectedValuesForPreset(factor, selectedPreset);
  const row = document.createElement("div");
  row.className = "factorial-row";
  row.setAttribute("role", "row");
  row.dataset.currentValues = JSON.stringify(initialValues || []);
  row.innerHTML = `
    <select class="form-select" data-factor-key></select>
    <select class="form-select" data-factor-preset></select>
    <div class="factor-level-cell">
      <div class="level-card-list" data-factor-values aria-label="${escapeHtml(t("factorial.levels"))}"></div>
      <div class="custom-level-control">
        <input class="form-control" type="text" data-level-custom />
        <button class="btn btn-outline-secondary inline-icon-button" type="button" data-level-add title="${escapeHtml(t("factorial.levelAdd"))}">
          <i class="ti ti-plus button-icon" aria-hidden="true"></i>
          <span>${escapeHtml(t("factorial.levelAdd"))}</span>
        </button>
      </div>
    </div>
    <span class="factor-count" data-factor-count>--</span>
    <button class="btn btn-outline-secondary inline-icon-button" type="button" data-factor-remove title="${escapeHtml(t("factorial.remove"))}">
      <i class="ti ti-x button-icon" aria-hidden="true"></i>
      <span data-i18n="factorial.remove">${escapeHtml(t("factorial.remove"))}</span>
    </button>
  `;
  factorialRows.appendChild(row);
  renderFactorOptions(row.querySelector("[data-factor-key]"), factor.key);
  updateCustomLevelPlaceholder(row);
  renderPresetOptions(row.querySelector("[data-factor-preset]"), factor, selectedPreset, initialValues);
  renderLevelCards(row, initialValues);
  updateFactorRowPreview(row);
}

function factorRowDefinition(key, values) {
  const factor = factorByKey(key);
  if (!factor) {
    return defaultFactorRowDefinition();
  }
  const preset = presetIdForValues(factor, values);
  return { key: factor.key, preset, values };
}

function defaultFactorRowDefinition() {
  const factor = visibleFactorCatalog()[0];
  return { key: factor.key, preset: factor.presets[0].id, values: factor.presets[0].values };
}

function renderFactorialModes() {
  if (!factorialModeList) {
    return;
  }
  factorialModeList.innerHTML = FACTORIAL_MODES.map((mode) => {
    const count = modeCombinationCount(mode);
    const active = factorialModeList.dataset.activeMode === mode.id ? " active" : "";
    return `
      <button class="factorial-mode${active}" type="button" data-factorial-mode="${escapeHtml(mode.id)}">
        <strong>${escapeHtml(localized(mode.label))}</strong>
        <span>${escapeHtml(localized(mode.note))}</span>
        <small>${escapeHtml(count)} ${escapeHtml(t("matrix.taskUnit"))}</small>
      </button>
    `;
  }).join("");
}

function applyFactorialMode(modeId) {
  const mode = FACTORIAL_MODES.find((item) => item.id === modeId);
  if (!mode) {
    return;
  }
  const definitions = mode.factors.map((item) => {
    const factor = factorByKey(item.key);
    const preset = presetById(factor, item.preset) || (factor && factor.presets[0]);
    return { key: factor.key, preset: preset.id, values: preset.values };
  });
  factorialTouched = true;
  factorialModeList.dataset.activeMode = mode.id;
  renderFactorialRows(definitions);
  renderFactorialModes();
  setFactorialStatus(t("factorial.modeApplied"), "ok");
}

function modeCombinationCount(mode) {
  return mode.factors.reduce((total, item) => {
    const factor = factorByKey(item.key);
    const preset = presetById(factor, item.preset);
    return total * ((preset && preset.values.length) || 1);
  }, 1);
}

function nextAvailableFactor() {
  const used = selectedFactorKeys();
  return visibleFactorCatalog().find((factor) => !used.has(factor.key));
}

function selectedFactorKeys(exceptRow = null) {
  const selected = new Set();
  for (const row of factorialRows.querySelectorAll(".factorial-row")) {
    if (row === exceptRow) {
      continue;
    }
    const key = row.querySelector("[data-factor-key]").value;
    if (key) {
      selected.add(key);
    }
  }
  return selected;
}

function renderFactorOptions(select, selectedKey) {
  select.innerHTML = visibleFactorCatalog().map((factor) => `
    <option value="${escapeHtml(factor.key)}"${factor.key === selectedKey ? " selected" : ""}>
      ${escapeHtml(displayParamKey(factor.key))}
    </option>
  `).join("");
}

function refreshFactorOptions() {
  for (const row of factorialRows.querySelectorAll(".factorial-row")) {
    const select = row.querySelector("[data-factor-key]");
    const selectedKey = select.value || visibleFactorCatalog()[0].key;
    const usedElsewhere = selectedFactorKeys(row);
    for (const option of select.options) {
      option.disabled = usedElsewhere.has(option.value);
    }
    if (usedElsewhere.has(selectedKey)) {
      const next = visibleFactorCatalog().find((factor) => !usedElsewhere.has(factor.key));
      if (next) {
        select.value = next.key;
        row.dataset.currentValues = "[]";
        renderPresetOptions(row.querySelector("[data-factor-preset]"), next, next.presets[0].id);
        renderLevelCards(row, next.presets[0].values);
      }
    }
    updateFactorRowPreview(row);
  }
}

function renderPresetOptions(select, factor, selectedPresetId, currentValues = []) {
  if (!factor) {
    select.innerHTML = "";
    return;
  }
  const hasPreset = Boolean(presetById(factor, selectedPresetId));
  const options = factor.presets.map((preset) => `
    <option value="${escapeHtml(preset.id)}"${preset.id === selectedPresetId ? " selected" : ""}>
      ${escapeHtml(localized(preset.label))}
    </option>
  `);
  if ((!hasPreset && currentValues.length) || selectedPresetId === "__current__" || selectedPresetId === "__custom__") {
    const specialId = selectedPresetId === "__custom__" ? "__custom__" : "__current__";
    const label = specialId === "__custom__"
      ? t("factorial.customSelection")
      : (currentLanguage === "zh" ? "当前矩阵水平" : "Current matrix levels");
    options.unshift(`<option value="${specialId}" selected>${escapeHtml(label)}</option>`);
  }
  select.innerHTML = options.join("");
}

function updateFactorRowPreview(row) {
  const values = valuesForFactorRow(row);
  row.querySelector("[data-factor-count]").textContent = values.length ? `×${values.length}` : "--";
  row.classList.toggle("empty-level-row", values.length === 0);
}

function valuesForFactorRow(row) {
  const factor = factorByKey(row.querySelector("[data-factor-key]").value);
  if (!factor) {
    return [];
  }
  const buttons = Array.from(row.querySelectorAll("button[data-level-card]"));
  if (buttons.length) {
    return buttons
      .filter((button) => button.getAttribute("aria-pressed") === "true")
      .map((button) => parseStoredLevelValue(button.dataset.valueJson))
      .filter((value) => typeof value !== "undefined");
  }
  return selectedValuesForPreset(factor, row.querySelector("[data-factor-preset]").value, readCurrentValues(row));
}

function renderLevelCards(row, selectedValues = []) {
  if (!row) {
    return;
  }
  const factor = factorByKey(row.querySelector("[data-factor-key]").value);
  const container = row.querySelector("[data-factor-values]");
  if (!factor || !container) {
    return;
  }
  const selected = Array.isArray(selectedValues) ? selectedValues : [];
  const selectedKeys = new Set(selected.map(valueKey));
  const candidates = candidateValuesForFactor(factor, selected);
  container.innerHTML = "";
  if (!candidates.length) {
    const empty = document.createElement("span");
    empty.className = "muted-chip";
    empty.textContent = "--";
    container.appendChild(empty);
    return;
  }
  for (const value of candidates) {
    const key = valueKey(value);
    const active = selectedKeys.has(key);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `level-card${active ? " active" : ""}`;
    button.dataset.levelCard = "true";
    button.dataset.valueJson = JSON.stringify(value);
    button.setAttribute("aria-pressed", active ? "true" : "false");
    button.textContent = displayParamValue(factor.key, value);
    button.title = displayParamValue(factor.key, value);
    container.appendChild(button);
  }
}

function selectedValuesForPreset(factor, presetId, fallbackValues = []) {
  if (!factor) {
    return [];
  }
  if (presetId === "__current__" || presetId === "__custom__") {
    return Array.isArray(fallbackValues) ? fallbackValues : [];
  }
  const preset = presetById(factor, presetId) || factor.presets[0];
  return preset ? preset.values : [];
}

function candidateValuesForFactor(factor, selectedValues = []) {
  if (factor.key === "window_id") {
    return Array.isArray(selectedValues) ? selectedValues : [];
  }
  const values = [];
  for (const value of factor.candidates || []) {
    pushUniqueValue(values, value);
  }
  for (const preset of factor.presets || []) {
    for (const value of preset.values || []) {
      pushUniqueValue(values, value);
    }
  }
  for (const value of selectedValues || []) {
    pushUniqueValue(values, value);
  }
  return values;
}

function pushUniqueValue(values, value) {
  const key = valueKey(value);
  if (!values.some((item) => valueKey(item) === key)) {
    values.push(value);
  }
}

function toggleLevelCard(button) {
  const active = button.getAttribute("aria-pressed") === "true";
  button.setAttribute("aria-pressed", active ? "false" : "true");
  button.classList.toggle("active", !active);
}

function addCustomLevel(row) {
  if (!row) {
    return;
  }
  const input = row.querySelector("[data-level-custom]");
  const rawValue = input.value.trim();
  if (!rawValue) {
    return;
  }
  let value;
  try {
    value = parseCustomLevelValue(rawValue, row.querySelector("[data-factor-key]").value);
  } catch (error) {
    const factorKey = row.querySelector("[data-factor-key]").value;
    setFactorialStatus(factorKey === "window_id" ? t("factorial.windowParseFail") : t("factorial.levelParseFail"), "warn");
    return;
  }
  const selected = valuesForFactorRow(row);
  pushUniqueValue(selected, value);
  row.dataset.currentValues = JSON.stringify(selected);
  markRowAsCustom(row, selected);
  renderLevelCards(row, selected);
  input.value = "";
  setFactorialStatus(t("factorial.idle"), "");
}

function markRowAsCustom(row, selectedValues = null) {
  if (!row) {
    return;
  }
  const values = selectedValues || valuesForFactorRow(row);
  row.dataset.currentValues = JSON.stringify(values);
  const factor = factorByKey(row.querySelector("[data-factor-key]").value);
  const presetSelect = row.querySelector("[data-factor-preset]");
  renderPresetOptions(presetSelect, factor, "__custom__", values);
}

function updateCustomLevelPlaceholder(row) {
  const input = row && row.querySelector("[data-level-custom]");
  if (!input) {
    return;
  }
  const factorKey = row.querySelector("[data-factor-key]")?.value || "";
  input.placeholder = customPlaceholderForFactor(factorKey);
}

function customPlaceholderForFactor(factorKey) {
  const zh = currentLanguage === "zh";
  const placeholders = {
    window_id: zh ? "例如 800-1100；拼接窗口 800-900;1000-1100" : "e.g. 800-1100; stitched: 800-900;1000-1100",
    activation_id: zh ? "例如 relu 或 gelu" : "e.g. relu or gelu",
    dropout: zh ? "例如 0.15" : "e.g. 0.15",
    learning_rate: zh ? "例如 0.0005" : "e.g. 0.0005",
    weight_decay: zh ? "例如 0.0001" : "e.g. 0.0001",
    model_id: zh ? "例如 cnn3" : "e.g. cnn3",
    pooling_id: zh ? "例如 POOL0" : "e.g. POOL0",
    preprocess_id: zh ? "例如 raw_standard 或 snv_standard" : "e.g. raw_standard or snv_standard",
    batch_size: zh ? "例如 32" : "e.g. 32",
    seed: zh ? "例如 20260616" : "e.g. 20260616",
    kernel_size: zh ? "例如 7" : "e.g. 7",
    epochs: zh ? "例如 40" : "e.g. 40",
    target_transform: zh ? "例如 linear 或 log1p" : "e.g. linear or log1p",
    loss_id: zh ? "例如 mse 或 smoothl1" : "e.g. mse or smoothl1",
    augmentation_id: zh ? "例如 加噪增强 或 组合增强" : "e.g. noise injection or combined augmentation",
    augmentation_multiplier: zh ? "例如 1、2、3" : "e.g. 1, 2, 3",
    channels: zh ? "例如 [16,32,64] 或 16,32,64" : "e.g. [16,32,64] or 16,32,64",
  };
  return placeholders[factorKey] || t("factorial.customPlaceholder");
}

function parseCustomLevelValue(text, factorKey) {
  const value = text.trim();
  if (!value) {
    throw new Error("Empty value");
  }
  if (factorKey === "window_id") {
    return parseCustomWindowValue(value);
  }
  if (factorKey === "augmentation_id") {
    return canonicalAugmentationId(value);
  }
  if (factorKey === "channels" && value.includes(",") && !value.startsWith("[") && !value.startsWith("{")) {
    const channels = value.split(",").map((part) => Number(part.trim()));
    if (channels.some((item) => !Number.isFinite(item))) {
      throw new Error("Invalid channels");
    }
    return channels;
  }
  if (value.startsWith("[") || value.startsWith("{") || value.startsWith("\"")) {
    return JSON.parse(value);
  }
  const numeric = Number(value);
  if (Number.isFinite(numeric) && value !== "") {
    return numeric;
  }
  return value;
}

function parseCustomWindowValue(value) {
  const intervals = value.split(";").map((part) => part.trim()).filter(Boolean);
  if (!intervals.length) {
    throw new Error("Empty window");
  }
  const idParts = [];
  for (const interval of intervals) {
    const match = interval.match(/^([0-9]+(?:\.[0-9]+)?)\s*-\s*([0-9]+(?:\.[0-9]+)?)$/);
    if (!match) {
      throw new Error("Invalid window");
    }
    const start = Number(match[1]);
    const end = Number(match[2]);
    if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
      throw new Error("Invalid window");
    }
    idParts.push(`${formatWindowNumber(start)}_${formatWindowNumber(end)}`);
  }
  return `CUSTOM_${idParts.join("__")}`;
}

function formatWindowNumber(value) {
  return String(Number(value.toFixed(3))).replace(".", "p");
}

function parseStoredLevelValue(valueJson) {
  try {
    return JSON.parse(valueJson || "null");
  } catch (error) {
    return undefined;
  }
}

function readCurrentValues(row) {
  try {
    const values = JSON.parse(row.dataset.currentValues || "[]");
    return Array.isArray(values) ? values : [];
  } catch (error) {
    return [];
  }
}

function valueKey(value) {
  return JSON.stringify(value);
}

function currentFactorRowDefinitions() {
  return Array.from(factorialRows.querySelectorAll(".factorial-row")).map((row) => {
    const key = row.querySelector("[data-factor-key]").value;
    const preset = row.querySelector("[data-factor-preset]").value;
    return { key, preset, values: valuesForFactorRow(row) };
  });
}

function rerenderFactorialRows() {
  const definitions = currentFactorRowDefinitions();
  renderFactorialRows(definitions.length ? definitions : [defaultFactorRowDefinition()]);
}

function factorByKey(key) {
  return FACTOR_CATALOG.find((factor) => factor.key === key);
}

function visibleFactorCatalog() {
  return FACTOR_CATALOG.filter((factor) => factor.key !== "cv_fold");
}

function presetById(factor, presetId) {
  return factor && factor.presets.find((preset) => preset.id === presetId);
}

function presetIdForValues(factor, values) {
  const normalized = JSON.stringify(values || []);
  const preset = factor.presets.find((item) => JSON.stringify(item.values) === normalized);
  return preset ? preset.id : "__current__";
}

function localized(value) {
  if (!value || typeof value !== "object") {
    return String(value || "");
  }
  return value[currentLanguage] || value.en || value.zh || "";
}

function baseParamKey(key) {
  const parts = String(key || "").split(".");
  return parts[parts.length - 1] || "";
}

function taskPrefixForParamKey(key) {
  const parts = String(key || "").split(".");
  return parts.length > 1 ? parts[0] : "";
}

function displayParamKey(key) {
  const cleanKey = baseParamKey(key);
  const prefix = taskPrefixForParamKey(key);
  const factor = factorByKey(cleanKey);
  const label = localized(PARAM_KEY_LABELS[cleanKey] || (factor && factor.label) || cleanKey);
  if (!prefix) {
    return label;
  }
  return `${displayParamValue("task", prefix)} · ${label}`;
}

function labelLookupKey(key) {
  const cleanKey = baseParamKey(key);
  return PARAM_VALUE_LABELS[cleanKey] ? cleanKey : (PARAM_VALUE_ALIASES[cleanKey] || cleanKey);
}

function displayParamValue(key, value) {
  if (value === null || typeof value === "undefined") {
    return "null";
  }
  if (Array.isArray(value)) {
    return value.join("-");
  }
  if (labelLookupKey(key) === "window_id") {
    const windowLabel = displayWindowValue(value);
    if (windowLabel) {
      return windowLabel;
    }
  }
  const lookupKey = labelLookupKey(key);
  const label = PARAM_VALUE_LABELS[lookupKey] && PARAM_VALUE_LABELS[lookupKey][String(value)];
  return label ? localized(label) : formatParamValue(value);
}

function canonicalAugmentationId(value) {
  const text = String(value || "").trim();
  const normalized = text.toLowerCase().replace(/\s+/g, "");
  const aliases = {
    aug0: "AUG0",
    "不使用数据增强": "AUG0",
    "不使用增强": "AUG0",
    "不增强": "AUG0",
    noaugmentation: "AUG0",
    none: "AUG0",
    aug1: "AUG1",
    "加噪增强": "AUG1",
    "噪声增强": "AUG1",
    noiseinjection: "AUG1",
    noise: "AUG1",
    aug2: "AUG2",
    "基线扰动增强": "AUG2",
    "基线扰动": "AUG2",
    baselineperturbation: "AUG2",
    baseline: "AUG2",
    aug3: "AUG3",
    "加噪+小幅波长位移": "AUG3",
    "加噪小幅波长位移": "AUG3",
    "小幅波长位移": "AUG3",
    wavelengthshift: "AUG3",
    shift: "AUG3",
    aug4: "AUG4",
    "组合增强": "AUG4",
    "组合增强（加噪+基线扰动+位移）": "AUG4",
    combinedaugmentation: "AUG4",
    combined: "AUG4",
  };
  const compactChinese = text.replace(/\s+/g, "").replace(/＋/g, "+").replace(/[()]/g, "（").replace(/）/g, "");
  return aliases[normalized] || aliases[compactChinese] || text;
}

function displayWindowValue(value) {
  const text = String(value);
  if (!text.startsWith("CUSTOM_")) {
    return "";
  }
  const intervals = text.slice("CUSTOM_".length).split("__").map((item) => {
    const [start, end] = item.split("_").map((part) => part.replace("p", "."));
    return `${start}-${end}`;
  }).join("; ");
  return currentLanguage === "zh" ? `自定义窗口 ${intervals} nm` : `Custom window ${intervals} nm`;
}

function displayParamValues(key, values) {
  const list = Array.isArray(values) ? values : [values];
  const visible = list.slice(0, 8).map((value) => displayParamValue(key, value)).join(", ");
  if (list.length > 8) {
    return `${visible}, ...`;
  }
  return visible || "--";
}

function displayFormula(formula) {
  return String(formula || "").replace(/([A-Za-z0-9_.]+)\((\d+)\)/g, (_match, key, count) => (
    `${displayParamKey(key)}(${count})`
  ));
}

function displayStatus(status) {
  const label = STATUS_LABELS[String(status || "idle")];
  return label ? localized(label) : String(status || "idle");
}

function updateFactorialDraftTotal() {
  if (!factorialRows) {
    return;
  }
  const designFactors = currentDesignFactors();
  let total = 1;
  let hasInvalidRow = false;
  for (const row of factorialRows.querySelectorAll(".factorial-row")) {
    updateFactorRowPreview(row);
  }
  for (const factor of designFactors) {
    const levels = factor.values;
    if (!factor.key || levels.length === 0) {
      hasInvalidRow = true;
      continue;
    }
    total *= levels.length;
  }
  const visibleTotal = hasInvalidRow ? null : total;
  factorialDraftTotal.textContent = visibleTotal === null ? "--" : String(visibleTotal);
  renderDraftMatrixPreview(visibleTotal, designFactors);
}

function renderDraftMatrixPreview(total, factors = currentDesignFactors()) {
  matrixTotal.textContent = total === null ? "--" : String(total);
  matrixFormula.textContent = factors.length
    ? factors.map((row) => `${displayParamKey(row.key)}(${row.values.length})`).join(" × ")
    : t("matrix.fixedOnly");
  matrixGridList.innerHTML = factors.length
    ? factors.map((row) => renderGridParamRow({ key: row.key, values: row.values, count: row.values.length })).join("")
    : `<p class="empty-hint">${t("matrix.gridEmpty")}</p>`;
  const fixedEntries = Object.entries(currentDraftFixedValues(factors));
  matrixFixedList.innerHTML = fixedEntries.length
    ? fixedEntries.map(renderFixedParamChip).join("")
    : `<p class="empty-hint">${t("matrix.fixedEmpty")}</p>`;
}

function renderFixedParamChip([key, value]) {
  return `<span class="fixed-chip" data-param-key="${escapeHtml(key)}"><strong>${escapeHtml(displayParamKey(key))}</strong><span class="fixed-chip-value">${escapeHtml(displayParamValue(key, value))}</span></span>`;
}

function collectFullFactorialFactors() {
  const factors = [];
  const seen = new Set();
  for (const factor of currentDesignFactors()) {
    const { key, values } = factor;
    if (!key) {
      throw new Error(t("factorial.emptyFactor"));
    }
    if (!values.length) {
      throw new Error(t("factorial.emptyLevels"));
    }
    if (seen.has(key)) {
      throw new Error(`${t("factorial.duplicate")}${displayParamKey(key)}`);
    }
    seen.add(key);
    factors.push({ key, values });
  }
  return factors;
}

function currentDesignFactors() {
  const modelFactors = Array.from(factorialRows.querySelectorAll(".factorial-row")).map((row) => ({
    key: row.querySelector("[data-factor-key]").value,
    values: valuesForFactorRow(row),
  })).filter((row) => row.key && row.values.length);
  const targetFactor = currentTargetTaskFactor();
  const splitFactor = currentSplitCvFactor();
  return [targetFactor, splitFactor, ...modelFactors].filter(Boolean);
}

function currentTargetTaskFactor() {
  const values = selectedTargetTasks();
  return values.length > 1 ? { key: "task", values } : null;
}

function currentDesignFixedOverrides(factors = currentDesignFactors()) {
  const factorKeys = new Set((factors || []).map((factor) => factor.key));
  const values = selectedTargetTasks();
  const overrides = values.length <= 1 ? { task: values[0] || "ppm" } : {};
  if (!factorKeys.has("window_id")) {
    overrides.window_id = defaultFixedValueForKey("window_id") || "WFULL_500_2500";
  }
  if (activeDataset && activeDataset.config) {
    overrides.dataset_config = activeDataset.config;
  } else if (workspaceState.datasetConfig) {
    overrides.dataset_config = workspaceState.datasetConfig;
  }
  return overrides;
}

function currentDraftFixedValues(factors = currentDesignFactors()) {
  const fixed = { ...(currentMatrixPreview && currentMatrixPreview.fixed ? currentMatrixPreview.fixed : {}) };
  for (const factor of factors) {
    delete fixed[factor.key];
  }
  return { ...fixed, ...currentDesignFixedOverrides(factors) };
}

function defaultFixedValueForKey(key) {
  if (currentMatrixPreview && currentMatrixPreview.fixed && currentMatrixPreview.fixed[key] !== undefined) {
    return currentMatrixPreview.fixed[key];
  }
  const gridRow = currentMatrixPreview && Array.isArray(currentMatrixPreview.grid)
    ? currentMatrixPreview.grid.find((row) => row.key === key)
    : null;
  if (gridRow && Array.isArray(gridRow.values) && gridRow.values.length) {
    return gridRow.values[0];
  }
  return "";
}

function designSignature(factors) {
  return JSON.stringify((factors || []).map((factor) => ({
    key: factor.key,
    values: (factor.values || [])
      .map((value) => JSON.stringify(value))
      .sort(),
  })).sort((a, b) => a.key.localeCompare(b.key)));
}

function previewDesignFactors() {
  if (!currentMatrixPreview || !Array.isArray(currentMatrixPreview.grid)) {
    return [];
  }
  return currentMatrixPreview.grid.map((row) => ({
    key: row.key,
    values: Array.isArray(row.values) ? row.values : [],
  })).filter((row) => row.key && row.values.length);
}

function designMatchesCurrentPreview() {
  return designSignature(currentDesignFactors()) === designSignature(previewDesignFactors());
}

function needsApplyBeforeCreate() {
  return factorialTouched || !designMatchesCurrentPreview();
}

function selectedTargetTasks() {
  const values = Array.from(targetToggles)
    .filter((toggle) => toggle.checked)
    .map((toggle) => TARGET_TASK_VALUES[toggle.dataset.targetToggle])
    .filter(Boolean);
  return values.length ? values : ["ppm"];
}

function currentSplitCvFactor() {
  const mode = currentSplitMode();
  if (!["cv", "train_only"].includes(mode)) {
    return null;
  }
  const values = selectedCvFolds();
  return values.length ? { key: "cv_fold", values } : null;
}

function selectedCvFolds() {
  if (!cvFoldOptions) {
    return [];
  }
  return Array.from(cvFoldOptions.querySelectorAll("button[data-cv-fold][aria-pressed='true']"))
    .map((button) => Number(button.dataset.cvFold))
    .filter((value) => Number.isFinite(value));
}

function currentSplitMode() {
  const checked = Array.from(splitModeInputs).find((input) => input.checked);
  return checked ? checked.value : "holdout";
}

async function applyFullFactorialDesign(options = {}) {
  const payload = formPayload(forms.matrix);
  if (!payload.config) {
    setFactorialStatus(t("matrix.previewFail"), "fail");
    return null;
  }
  let factors = [];
  try {
    factors = collectFullFactorialFactors();
  } catch (error) {
    setFactorialStatus(error.message, "warn");
    return null;
  }
  if (factorialApply) {
    factorialApply.disabled = true;
  }
  setFactorialStatus(t("factorial.applying"), "pending");
  try {
    const data = await fetchJson("/api/matrix/full-factorial", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: payload.config, factors, fixed: currentDesignFixedOverrides(factors) }),
    });
    forms.matrix.elements.config.value = data.config;
    currentMatrixPreview = data.preview;
    factorialTouched = false;
    renderMatrixPreview(data.preview);
    setFactorialStatus(t("factorial.applied"), "ok");
    if (options.updateMatrixStatus !== false) {
      setMatrixStatus(`${t("matrix.previewReady")}：${data.preview.total_combinations} ${t("matrix.taskUnit")}`, "ok");
    }
    if (!options.silent) {
      appendResult("Full factorial design", "ok", `combinations=${data.preview.total_combinations}, ${displayFormula(data.preview.formula)}`, data);
    }
    return data;
  } catch (error) {
    setFactorialStatus(`${t("factorial.fail")}：${error.message}`, "fail");
    appendResult("Full factorial design", "fail", error.message, { error: error.message, payload: { config: payload.config, factors } });
    return null;
  } finally {
    if (factorialApply) {
      factorialApply.disabled = false;
    }
  }
}

function setFactorialStatus(text, state) {
  factorialStatus.removeAttribute("data-i18n");
  factorialStatus.textContent = text;
  factorialStatus.className = `check-message ${state || ""}`.trim();
}

function formatParamValues(values) {
  const list = Array.isArray(values) ? values : [values];
  const visible = list.slice(0, 8).map(formatParamValue).join(", ");
  if (list.length > 8) {
    return `${visible}, ...`;
  }
  return visible || "--";
}

function formatParamValue(value) {
  if (value === null || typeof value === "undefined") {
    return "null";
  }
  if (Array.isArray(value)) {
    return value.join("-");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

async function fileToBase64(file) {
  const buffer = await file.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
  }
  return btoa(binary);
}

function renderImportSummary(data) {
  const files = data.files || [];
  const generated = data.generated || {};
  const configLine = renderImportStatus(data, generated);
  const generatedFacts = generated.status === "ready"
    ? `<div class="import-facts">
        <span>${currentLanguage === "zh" ? "样品" : "Samples"}: ${escapeHtml(generated.samples || "--")}</span>
        <span>${currentLanguage === "zh" ? "波长点" : "Wavelengths"}: ${escapeHtml(generated.wavelengths || "--")}</span>
        <span>${currentLanguage === "zh" ? "目标" : "Targets"}: ${escapeHtml(Object.keys(generated.targets || {}).join(", ") || "--")}</span>
      </div>`
    : "";
  const warnings = Array.isArray(generated.warnings) && generated.warnings.length
    ? `<ul class="import-warnings">${generated.warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
    : "";
  importSummary.innerHTML = `
    ${configLine}
    ${generatedFacts}
    ${warnings}
    <div class="import-file-grid">
      ${files.map((file) => renderImportFile(file)).join("")}
    </div>
  `;
  updateDatasetConfirmState(generated.status === "ready" || Boolean(data.dataset_config));
}

function renderImportStatus(data, generated) {
  if (generated.status === "ready") {
    return `<div class="import-ready">${currentLanguage === "zh" ? "已从 CSV/NPZ 自动准备可训练数据集" : "Trainable dataset prepared automatically from CSV/NPZ"}</div>`;
  }
  if (data.dataset_config) {
    return `<div class="import-ready">${currentLanguage === "zh" ? "已识别数据配置" : "Dataset config detected"}</div>`;
  }
  if (generated.status === "needs_review") {
    return `<div class="import-warning">${escapeHtml(generated.message || (currentLanguage === "zh" ? "导入内容需要检查" : "Import needs review"))}</div>`;
  }
  return `<div class="import-warning">${currentLanguage === "zh" ? "还缺光谱 CSV/NPZ 或监督标签 CSV" : "Drop a spectral CSV/NPZ and a supervision CSV"}</div>`;
}

function renderImportFile(file) {
  const preview = file.preview || {};
  const previewText = preview.keys
    ? preview.keys.join(", ")
    : preview.columns
      ? preview.columns.join(", ")
      : preview.arrays
        ? Object.keys(preview.arrays).join(", ")
        : "";
  return `
    <div class="import-file-card">
      <strong>${escapeHtml(file.name)}</strong>
      <span>${escapeHtml(file.kind)} · ${formatBytes(file.size)}</span>
      <small title="${escapeHtml(file.path)}">${escapeHtml(previewText || file.path)}</small>
    </div>
  `;
}

function updateDatasetConfirmState(importReady = null) {
  const ready = importReady === null
    ? datasetConfirm.dataset.importReady === "true"
    : Boolean(importReady);
  datasetConfirm.dataset.importReady = ready ? "true" : "false";
  const hasCode = Boolean(datasetCodeInput.value.trim());
  datasetConfirm.disabled = !(ready && hasCode);
  if (!ready) {
    setDatasetLockStatus(t("datasetCode.waiting"), "warn");
    return;
  }
  if (!hasCode) {
    setDatasetLockStatus(t("datasetCode.ready"), "pending");
  }
}

function confirmActiveDataset() {
  const code = datasetCodeInput.value.trim();
  if (!code) {
    setDatasetLockStatus(t("datasetCode.needCode"), "warn");
    return;
  }
  activeDataset = {
    code,
    config: forms.dataset.elements.config.value || "",
    locked_at: new Date().toISOString(),
  };
  localStorage.setItem("spectramatrix_active_dataset", JSON.stringify(activeDataset));
  saveWorkspaceState({ datasetCode: code, datasetConfig: activeDataset.config });
  setDatasetLockStatus(`${t("datasetCode.locked")}${code}`, "ok");
  renderActiveDataset();
  appendResult("Dataset locked", "ok", code, activeDataset);
}

function setDatasetLockStatus(text, state) {
  datasetLockStatus.removeAttribute("data-i18n");
  datasetLockStatus.textContent = text;
  datasetLockStatus.className = `check-message ${state || ""}`.trim();
}

function renderActiveDataset() {
  if (!activeDataset || !activeDataset.code) {
    activeDatasetCode.textContent = currentLanguage === "zh" ? "尚未确认" : "Not confirmed";
    return;
  }
  activeDatasetCode.textContent = activeDataset.code;
  activeDatasetCode.title = activeDataset.config || activeDataset.code;
}

function updateTargetRuleVisibility() {
  const selected = targetSelectionSnapshot();
  for (const card of document.querySelectorAll("[data-target-card]")) {
    const key = card.dataset.targetCard;
    card.classList.toggle("active", Boolean(selected[key]));
  }
  const binaryRule = document.querySelector("[data-rule-section='binary']");
  const triRule = document.querySelector("[data-rule-section='tri']");
  if (binaryRule) {
    binaryRule.hidden = !selected.binary;
  }
  if (triRule) {
    triRule.hidden = !selected.tri;
  }
  if (targetRuleEmpty) {
    targetRuleEmpty.hidden = selected.binary || selected.tri;
  }
}

function targetSelectionSnapshot() {
  const snapshot = {};
  for (const toggle of targetToggles) {
    snapshot[toggle.dataset.targetToggle] = toggle.checked;
  }
  return snapshot;
}

function updateSplitModeUi() {
  const mode = currentSplitMode();
  if (splitModeList) {
    for (const card of splitModeList.querySelectorAll("[data-split-mode-card]")) {
      card.classList.toggle("active", card.dataset.splitModeCard === mode);
    }
  }
  const validationBlock = document.querySelector("[data-split-block='validation']");
  const testBlock = document.querySelector("[data-split-block='test']");
  const validationEnabled = mode === "holdout";
  const testEnabled = mode !== "train_only";
  if (validationBlock) {
    validationBlock.classList.toggle("disabled", !validationEnabled);
  }
  if (testBlock) {
    testBlock.classList.toggle("disabled", !testEnabled);
  }
  if (splitValRatio) {
    splitValRatio.disabled = !validationEnabled;
    splitValRatio.value = validationEnabled ? (splitValRatio.value === "0" ? "16" : splitValRatio.value) : "0";
  }
  if (splitTestRatio) {
    splitTestRatio.disabled = !testEnabled;
    splitTestRatio.value = testEnabled ? (splitTestRatio.value === "0" ? "20" : splitTestRatio.value) : "0";
  }
  if (splitTrainRatio) {
    if (mode === "holdout") {
      splitTrainRatio.value = splitTrainRatio.value === "100" ? "64" : splitTrainRatio.value;
    } else if (mode === "cv") {
      splitTrainRatio.value = "80";
    } else {
      splitTrainRatio.value = "100";
    }
  }
  if (cvFoldPanel) {
    cvFoldPanel.hidden = !["cv", "train_only"].includes(mode);
  }
}

function splitSelectionSnapshot() {
  return {
    mode: currentSplitMode(),
    train_ratio: splitTrainRatio ? splitTrainRatio.value : "",
    validation_ratio: splitValRatio ? splitValRatio.value : "",
    test_ratio: splitTestRatio ? splitTestRatio.value : "",
    cv_folds: selectedCvFolds(),
  };
}

function currentTrainingDesignState() {
  return {
    environment: {
      framework: trainingFramework ? trainingFramework.value : "",
      device: trainingDevice ? trainingDevice.value : "",
      precision: trainingPrecision ? trainingPrecision.value : "",
      export_target: trainingExportTarget ? trainingExportTarget.value : "",
    },
    targets: targetSelectionSnapshot(),
    rules: {
      binary_threshold: binaryThreshold ? binaryThreshold.value : "",
      tri_low_max: triLowMax ? triLowMax.value : "",
      tri_mid_max: triMidMax ? triMidMax.value : "",
    },
    split: splitSelectionSnapshot(),
    factors: factorialRows ? currentFactorRowDefinitions() : [],
  };
}

function currentWorkshopDesignState() {
  return {
    backend: "mlp",
    strategy: "freeze_cnn_embeddings",
    mlp_layers: workshopMlpLayers ? workshopMlpLayers.value : "2",
    hidden_width: workshopHiddenWidth ? workshopHiddenWidth.value : "128",
    activation: workshopActivation ? workshopActivation.value : "gelu",
    dropout: workshopDropout ? workshopDropout.value : "0.3",
    note: currentLanguage === "zh" ? "冻结 1D-CNN backbone，提取 embedding 后训练 MLP 后端。" : "Freeze the 1D-CNN backbone, extract embeddings, then train an MLP backend.",
  };
}

function persistTrainingDesignDraft() {
  workspaceState = {
    ...workspaceState,
    trainingDesign: currentTrainingDesignState(),
    workshopDesign: currentWorkshopDesignState(),
    updatedAt: new Date().toISOString(),
  };
  localStorage.setItem("spectramatrix_workspace_state", JSON.stringify(workspaceState));
  scheduleProjectAutosave();
}

function applyTrainingDesignState(design) {
  if (!design || typeof design !== "object") {
    return;
  }
  const environment = design.environment || {};
  setSelectValue(trainingFramework, environment.framework);
  setSelectValue(trainingDevice, environment.device);
  setSelectValue(trainingPrecision, environment.precision);
  setSelectValue(trainingExportTarget, environment.export_target);

  const targets = design.targets || {};
  for (const toggle of targetToggles) {
    const key = toggle.dataset.targetToggle;
    if (Object.prototype.hasOwnProperty.call(targets, key)) {
      toggle.checked = Boolean(targets[key]);
    }
  }

  const rules = design.rules || {};
  setInputValue(binaryThreshold, rules.binary_threshold);
  setInputValue(triLowMax, rules.tri_low_max);
  setInputValue(triMidMax, rules.tri_mid_max);

  const split = design.split || {};
  if (split.mode) {
    for (const input of splitModeInputs) {
      input.checked = input.value === split.mode;
    }
  }
  setInputValue(splitTrainRatio, split.train_ratio);
  setInputValue(splitValRatio, split.validation_ratio);
  setInputValue(splitTestRatio, split.test_ratio);
  if (Array.isArray(split.cv_folds) && cvFoldOptions) {
    const selected = new Set(split.cv_folds.map(String));
    for (const button of cvFoldOptions.querySelectorAll("button[data-cv-fold]")) {
      const active = selected.has(String(button.dataset.cvFold));
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    }
  }

  if (Array.isArray(design.factors) && design.factors.length) {
    renderFactorialRows(design.factors);
    factorialTouched = true;
  }
  updateTargetRuleVisibility();
  updateSplitModeUi();
  updateFactorialDraftTotal();
}

function applyWorkshopDesignState(design) {
  if (!design || typeof design !== "object") {
    renderWorkshopPlan();
    return;
  }
  setSelectValue(workshopMlpLayers, design.mlp_layers);
  setSelectValue(workshopHiddenWidth, design.hidden_width);
  setSelectValue(workshopActivation, design.activation);
  setSelectValue(workshopDropout, design.dropout);
  renderWorkshopPlan(design);
}

function renderWorkshopPlan(design = null) {
  if (!workshopCurrentPlan) {
    return;
  }
  const state = design || currentWorkshopDesignState();
  const title = t("workshop.currentPlan");
  const note = state.note;
  workshopCurrentPlan.innerHTML = `
    <strong>${escapeHtml(title)}</strong>
    <span>${escapeHtml(note || "")}</span>
    <div>
      <em>MLP ${escapeHtml(state.mlp_layers || "2")} × ${escapeHtml(state.hidden_width || "128")}</em>
      <em>${escapeHtml(displayParamValue("activation_id", state.activation || "gelu"))}</em>
      <em>Dropout ${escapeHtml(state.dropout || "0.3")}</em>
    </div>
  `;
}

function setSelectValue(select, value) {
  if (!select || value === null || typeof value === "undefined" || value === "") {
    return;
  }
  const hasOption = Array.from(select.options).some((option) => option.value === String(value));
  if (hasOption) {
    select.value = String(value);
  }
}

function setInputValue(input, value) {
  if (!input || value === null || typeof value === "undefined" || value === "") {
    return;
  }
  input.value = value;
}

async function startQueueJob(payload) {
  const submitter = document.activeElement;
  if (submitter instanceof HTMLButtonElement) {
    submitter.disabled = true;
  }
  stopQueuePolling();
  setQueueJobStatus({ status: "starting", request: payload });
  try {
    const data = await fetchJson("/api/queue/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    appendResult("Queue start", "ok", summarizeOutput(data), data);
    activeQueueJobId = data.job_id || "";
    setQueueJobStatus(data);
    if (data.request && data.request.tasks) {
      forms.monitor.elements.tasks.value = data.request.tasks;
      saveWorkspaceState({ tasksDir: data.request.tasks, queueJobId: data.job_id || "" });
    }
    await refreshTasks({ silent: true });
    pollQueueJob(data.job_id);
  } catch (error) {
    setQueueJobStatus({ status: "failed", error: error.message, request: payload });
    appendResult("Queue start", "fail", error.message, { error: error.message, payload });
  } finally {
    if (submitter instanceof HTMLButtonElement) {
      submitter.disabled = false;
    }
  }
}

async function stopQueueJob() {
  if (!activeQueueJobId) {
    setQueueJobStatus({
      status: "idle",
      error: currentLanguage === "zh" ? "没有正在运行的训练任务。" : "No active training job.",
    });
    return;
  }
  if (queueStopButton) {
    queueStopButton.disabled = true;
  }
  try {
    const data = await fetchJson(`/api/queue/jobs/${encodeURIComponent(activeQueueJobId)}/stop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    setQueueJobStatus(data);
    appendResult("Queue stop", "ok", summarizeOutput(data), data);
    await refreshTasks({ silent: true });
  } catch (error) {
    setQueueJobStatus({ status: "failed", error: error.message, job_id: activeQueueJobId });
    appendResult("Queue stop", "fail", error.message, { error: error.message, job_id: activeQueueJobId });
  }
}

function pollQueueJob(jobId) {
  queueJobPoller = window.setInterval(async () => {
    try {
      const data = await fetchJson(`/api/queue/jobs/${encodeURIComponent(jobId)}`);
      setQueueJobStatus(data);
      await refreshTasks({ silent: true });
      if (["succeeded", "failed", "cancelled"].includes(data.status)) {
        stopQueuePolling();
        const status = data.status === "succeeded" ? "ok" : "fail";
        saveWorkspaceState({ queueStatus: data.status, queueResult: data.result || null });
        appendResult("Queue job", status, summarizeOutput(data.result || data), data);
      }
    } catch (error) {
      stopQueuePolling();
      setQueueJobStatus({ status: "failed", error: error.message });
      appendResult("Queue job", "fail", error.message, { error: error.message, job_id: jobId });
    }
  }, 1500);
}

function stopQueuePolling() {
  if (queueJobPoller) {
    window.clearInterval(queueJobPoller);
    queueJobPoller = null;
  }
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, options);
  const text = await response.text();
  let data = {};
  if (text) {
    data = JSON.parse(text);
  }
  if (!response.ok) {
    const detail = data.detail || response.statusText;
    recordDiagnosticEvent("api.error", {
      path,
      method: options.method || "GET",
      http_status: response.status,
      detail,
    });
    throw new Error(detail);
  }
  recordDiagnosticEvent("api.ok", {
    path,
    method: options.method || "GET",
    http_status: response.status,
  });
  return data;
}

function setDefaults(defaults) {
  rootPath.textContent = shortPath(defaults.root);
  rootPath.title = defaults.root;
  demoProjectPath = defaults.demo_project_path || "";
  forms.dataset.elements.config.value = defaults.dataset_config;
  forms.dataset.elements.out.value = defaults.dataset_inspect_out;
  forms.matrix.elements.config.value = defaults.matrix_config;
  forms.matrix.elements.out.value = defaults.matrix_out;
  if (forms.matrix.elements.max_tasks) {
    forms.matrix.elements.max_tasks.value = defaults.matrix_max_tasks ?? "";
  }
  forms.queue.elements.tasks.value = defaults.runs_dir;
  forms.queue.elements.max_tasks.value = defaults.queue_max_tasks ?? "";
  forms.queue.elements.dry_run.checked = Boolean(defaults.queue_dry_run);
  forms.queue.elements.rerun_failed.checked = false;
  forms.monitor.elements.tasks.value = defaults.monitor_tasks_dir;
  forms.scan.elements.runs.value = defaults.runs_dir;
  forms.scan.elements.out.value = defaults.registry_out;
  forms.candidate.elements.registry.value = workspaceState.registry || "";
  forms.candidate.elements.metric.value = "val_rmse";
  forms.candidate.elements.out.value = defaults.candidates_out;
  forms.candidate.elements.direction.value = "min";
  forms.aggregate.elements.registry.value = workspaceState.registry || "";
  forms.aggregate.elements.metric.value = "val_rmse";
  forms.aggregate.elements.group_by.value = defaults.group_by.join(",");
  forms.aggregate.elements.out.value = defaults.aggregate_out;
  forms.aggregate.elements.direction.value = "min";
  if (logRecorderPath && !logRecorderPath.value) {
    logRecorderPath.value = defaults.diagnostics_out || "";
  }
  if (projectFilePath) {
    projectFilePath.value = workspaceState.projectPath && !isDefaultAutosaveProjectPath(workspaceState.projectPath)
      ? workspaceState.projectPath
      : "";
    projectFilePath.placeholder = defaults.project_path || "";
  }
  renderActiveDataset();
  renderDiagnosticsRecorderState();
  renderResultSelectionState();
}

function saveWorkspaceState(patch) {
  workspaceState = {
    ...workspaceState,
    ...patch,
    updatedAt: new Date().toISOString(),
  };
  localStorage.setItem("spectramatrix_workspace_state", JSON.stringify(workspaceState));
  scheduleProjectAutosave();
}

function buildProjectState() {
  const projectPath = projectFilePath ? projectFilePath.value.trim() : (workspaceState.projectPath || "");
  return {
    name: activeDataset && activeDataset.code ? activeDataset.code : "SpectraMatrix Project",
    project_file: projectPath,
    dataset_code: activeDataset && activeDataset.code ? activeDataset.code : (workspaceState.datasetCode || ""),
    dataset_config: activeDataset && activeDataset.config ? activeDataset.config : (workspaceState.datasetConfig || forms.dataset.elements.config.value || ""),
    import_manifest: workspaceState.importManifest || "",
    training_design: currentTrainingDesignState(),
    workshop_design: currentWorkshopDesignState(),
    matrix_config: forms.matrix.elements.config.value || "",
    matrix_out: forms.matrix.elements.out.value || "",
    matrix_dir: workspaceState.matrixDir || "",
    task_index: workspaceState.taskIndex || "",
    manifest: workspaceState.matrixManifest || "",
    tasks_dir: forms.queue.elements.tasks.value || forms.monitor.elements.tasks.value || workspaceState.tasksDir || "",
    registry: forms.candidate.elements.registry.value || workspaceState.registry || "",
    selected_output_task_id: selectedOutputTaskId || workspaceState.selectedOutputTaskId || "",
    queue_job_id: activeQueueJobId || "",
    queue_status: queueJobStatus ? (queueJobStatus.dataset.status || "") : "",
    queue_result: workspaceState.queueResult || null,
    outputs: compactProjectOutputs(workspaceState.outputs || null),
  };
}

function compactProjectOutputs(outputs) {
  if (!outputs || typeof outputs !== "object") {
    return null;
  }
  const compact = { ...outputs };
  if (compact.prediction_summary && typeof compact.prediction_summary === "object") {
    compact.prediction_summary = { ...compact.prediction_summary };
    delete compact.prediction_summary.points;
  }
  return compact;
}

function handleProjectSaveClick() {
  if (hasExplicitProjectFile()) {
    saveProjectFile({ manual: true });
    return;
  }
  openProjectSaveDialog({ saveAs: false });
}

function hasExplicitProjectFile() {
  const path = currentProjectFilePath();
  return Boolean(path && !isDefaultAutosaveProjectPath(path));
}

function currentProjectFilePath() {
  return projectFilePath ? projectFilePath.value.trim() : (workspaceState.projectPath || "");
}

function isDefaultAutosaveProjectPath(path) {
  const normalized = String(path || "").replace(/\\/g, "/");
  return normalized.endsWith("/projects/autosave.spectramatrix.json") || normalized === "autosave.spectramatrix.json";
}

function defaultProjectSaveName() {
  const existing = currentProjectFilePath();
  if (existing && !isDefaultAutosaveProjectPath(existing)) {
    return fileStemFromPath(existing);
  }
  const datasetCode = activeDataset && activeDataset.code ? activeDataset.code : (workspaceState.datasetCode || "");
  if (datasetCode) {
    return cleanProjectFilename(`${datasetCode}_工程`);
  }
  return cleanProjectFilename(`SpectraMatrix_${new Date().toISOString().slice(0, 10)}`);
}

function fileStemFromPath(path) {
  const name = String(path || "").split(/[\\/]/).pop() || "";
  return name.replace(/\.spectramatrix\.json$/i, "").replace(/\.json$/i, "") || "SpectraMatrix_Project";
}

function cleanProjectFilename(name) {
  return String(name || "SpectraMatrix_Project")
    .trim()
    .replace(/\.spectramatrix\.json$/i, "")
    .replace(/\.json$/i, "")
    .replace(/[\\/:*?"<>|]+/g, "_")
    .replace(/\s+/g, "_")
    .replace(/^[_\-.]+|[_\-.]+$/g, "") || "SpectraMatrix_Project";
}

function openProjectSaveDialog(options = {}) {
  pendingProjectSaveMode = options.saveAs ? "saveAs" : "save";
  if (!projectSaveDialog || !projectSaveNameInput) {
    const name = window.prompt(t("project.saveDialogName"), defaultProjectSaveName());
    if (name && name.trim()) {
      saveProjectFile({ manual: true, filename: name.trim(), saveAs: true });
    }
    return;
  }
  if (projectSaveDialogTitle) {
    projectSaveDialogTitle.textContent = options.saveAs ? t("project.saveDialogTitleAs") : t("project.saveDialogTitle");
  }
  if (projectSaveDialogHint) {
    projectSaveDialogHint.textContent = t("project.saveDialogHint");
  }
  projectSaveNameInput.value = defaultProjectSaveName();
  projectSaveNameInput.setAttribute("placeholder", "SpectraMatrix_Project");
  projectSaveDialog.showModal();
  projectSaveNameInput.focus();
  projectSaveNameInput.select();
}

function closeProjectSaveDialog() {
  if (projectSaveDialog && projectSaveDialog.open) {
    projectSaveDialog.close();
  }
}

function confirmProjectSaveDialog() {
  const rawName = projectSaveNameInput ? projectSaveNameInput.value.trim() : "";
  if (!rawName) {
    setProjectStatus(t("project.saveNeedName"), "warn");
    return;
  }
  const filename = cleanProjectFilename(rawName);
  closeProjectSaveDialog();
  saveProjectFile({ manual: true, filename, saveAs: pendingProjectSaveMode === "saveAs" || !hasExplicitProjectFile() });
}

function scheduleProjectAutosave() {
  if (!projectFilePath || !hasExplicitProjectFile()) {
    return;
  }
  if (projectAutosaveTimer) {
    window.clearTimeout(projectAutosaveTimer);
  }
  projectAutosaveTimer = window.setTimeout(() => {
    saveProjectFile({ manual: false });
  }, 700);
}

async function saveProjectFile(options = {}) {
  if (!projectFilePath) {
    return null;
  }
  const project = buildProjectState();
  const filename = options.filename ? cleanProjectFilename(options.filename) : "";
  const pathForSave = filename ? "" : project.project_file;
  if (!pathForSave && !filename && !project.matrix_dir) {
    return null;
  }
  if (options.manual && projectStatus) {
    setProjectStatus(currentLanguage === "zh" ? "正在保存工程..." : "Saving project...", "pending");
  }
  try {
    const data = await fetchJson("/api/project/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: pathForSave || "", filename: filename || null, project }),
    });
    projectFilePath.value = data.path || project.project_file || "";
    if (projectSelectedFile && data.path) {
      projectSelectedFile.removeAttribute("data-i18n");
      projectSelectedFile.textContent = shortPath(data.path);
      projectSelectedFile.title = data.path;
    }
    workspaceState = {
      ...workspaceState,
      projectPath: data.path || project.project_file || "",
      projectAutosaveEnabled: true,
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem("spectramatrix_workspace_state", JSON.stringify(workspaceState));
    const statusLabel = options.saveAs ? t("project.saveAsSaved") : t("project.saved");
    setProjectStatus(`${statusLabel} ${shortPath(data.path || "")}`, "ok");
    if (options.manual) {
      appendResult("Project save", "ok", data.path || "", data);
    }
    return data;
  } catch (error) {
    setProjectStatus(error.message, "fail");
    if (options.manual) {
      appendResult("Project save", "fail", error.message, { error: error.message, project });
    }
    return null;
  }
}

async function openProjectFromFile(file) {
  if (!file) {
    return;
  }
  if (!file.name.endsWith(".spectramatrix.json")) {
    setProjectStatus(
      currentLanguage === "zh" ? "请选择 .spectramatrix.json 工程文件。" : "Choose a .spectramatrix.json project file.",
      "warn",
    );
    return;
  }
  if (projectSelectedFile) {
    projectSelectedFile.removeAttribute("data-i18n");
    projectSelectedFile.textContent = `${file.name} · ${formatBytes(file.size)}`;
  }
  setProjectStatus(currentLanguage === "zh" ? "正在读取工程文件..." : "Reading project file...", "pending");
  try {
    const data = await fetchJson("/api/project/import-file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        file: {
          name: file.name,
          content_base64: await fileToBase64(file),
          size: file.size,
          mime_type: file.type || "application/json",
        },
      }),
    });
    await applyProjectState(data.project || {}, data.path || file.name);
    setProjectStatus(`${t("project.opened")} ${shortPath(data.path || file.name)}`, "ok");
    appendResult("Project file import", "ok", data.path || file.name, data);
  } catch (error) {
    setProjectStatus(error.message, "fail");
    appendResult("Project file import", "fail", error.message, { error: error.message, file: file.name });
  }
}

async function openProjectFile() {
  const path = projectFilePath ? projectFilePath.value.trim() : "";
  if (!path) {
    setProjectStatus(currentLanguage === "zh" ? "请选择工程文件，或在高级路径里填写路径。" : "Choose a project file, or enter a path in Advanced.", "warn");
    return;
  }
  setProjectStatus(currentLanguage === "zh" ? "正在打开工程..." : "Opening project...", "pending");
  try {
    const data = await fetchJson("/api/project/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    await applyProjectState(data.project || {}, data.path || path);
    setProjectStatus(`${t("project.opened")} ${shortPath(data.path || path)}`, "ok");
    appendResult("Project open", "ok", data.path || path, data);
  } catch (error) {
    setProjectStatus(error.message, "fail");
    appendResult("Project open", "fail", error.message, { error: error.message, path });
  }
}

async function openDemoProject() {
  if (!demoProjectPath) {
    setProjectStatus(
      currentLanguage === "zh" ? "示例工程路径尚未加载，请先刷新默认配置。" : "Demo project path is not loaded. Refresh defaults first.",
      "warn",
    );
    return;
  }
  if (projectFilePath) {
    projectFilePath.value = demoProjectPath;
  }
  await openProjectFile();
  setActiveView("outputs");
}

function useCurrentTrainingResults(options = {}) {
  const tasks =
    forms.queue.elements.tasks.value ||
    forms.monitor.elements.tasks.value ||
    forms.scan.elements.runs.value ||
    workspaceState.tasksDir ||
    "";
  const registry =
    forms.candidate.elements.registry.value ||
    workspaceState.registry ||
    "";
  if (tasks) {
    forms.scan.elements.runs.value = tasks;
    forms.queue.elements.tasks.value = forms.queue.elements.tasks.value || tasks;
    forms.monitor.elements.tasks.value = forms.monitor.elements.tasks.value || tasks;
  }
  if (registry) {
    forms.candidate.elements.registry.value = registry;
    forms.aggregate.elements.registry.value = registry;
  }
  if (!options.silent) {
    appendResult(
      "Result source",
      tasks || registry ? "ok" : "warn",
      tasks || registry
        ? (currentLanguage === "zh" ? "已读取当前工程的训练结果来源。" : "Loaded result source from the current project.")
        : (currentLanguage === "zh" ? "当前工程还没有训练任务或结果表。" : "The current project has no task folder or result table yet."),
      { tasks, registry },
    );
  }
  renderResultSelectionState();
}

function setResultMetricChoice(metric, direction) {
  if (!metric) {
    return;
  }
  for (const button of metricChoices) {
    button.classList.toggle("active", button.dataset.metricChoice === metric);
  }
  forms.candidate.elements.metric.value = metric;
  forms.aggregate.elements.metric.value = metric;
  forms.candidate.elements.direction.value = direction || "auto";
  forms.aggregate.elements.direction.value = direction || "auto";
  renderResultSelectionState();
}

function setResultTopChoice(value) {
  const top = Number(value || 5);
  for (const button of topChoices) {
    button.classList.toggle("active", Number(button.dataset.topChoice || 0) === top);
  }
  forms.candidate.elements.top.value = String(top);
  renderResultSelectionState();
}

function renderResultSelectionState() {
  const tasks = forms.scan.elements.runs.value || forms.queue.elements.tasks.value || workspaceState.tasksDir || "";
  const registry = forms.candidate.elements.registry.value || workspaceState.registry || "";
  const metric = forms.candidate.elements.metric.value || "";
  const top = forms.candidate.elements.top.value || "5";
  if (resultTaskSource) {
    resultTaskSource.textContent = tasks ? shortPath(tasks) : (currentLanguage === "zh" ? "还没有训练任务" : "No task folder");
    resultTaskSource.title = tasks;
  }
  if (resultRegistrySource) {
    resultRegistrySource.textContent = registry ? shortPath(registry) : (currentLanguage === "zh" ? "先扫描生成结果表" : "Scan to create a result table");
    resultRegistrySource.title = registry;
  }
  if (resultSelectionState) {
    if (registry) {
      resultSelectionState.textContent = currentLanguage === "zh"
        ? `可以筛选：${displayMetricLabel(metric)}，保留 Top ${top}`
        : `Ready: ${displayMetricLabel(metric)}, keep Top ${top}`;
      resultSelectionState.className = "ready";
    } else if (tasks) {
      resultSelectionState.textContent = currentLanguage === "zh" ? "请先扫描训练结果" : "Scan training results first";
      resultSelectionState.className = "pending";
    } else {
      resultSelectionState.textContent = currentLanguage === "zh" ? "请先完成模型训练" : "Run training first";
      resultSelectionState.className = "warn";
    }
  }
}

function displayMetricLabel(metric) {
  const normalized = String(metric || "val_rmse");
  const labels = {
    val_rmse: currentLanguage === "zh" ? "验证 RMSE" : "Validation RMSE",
    val_mae: currentLanguage === "zh" ? "验证 MAE" : "Validation MAE",
    val_balanced_accuracy: "Balanced Accuracy",
  };
  return labels[normalized] || normalized || (currentLanguage === "zh" ? "自动识别指标" : "Auto metric");
}

async function applyProjectState(project, path) {
  if (projectFilePath) {
    projectFilePath.value = path || project.project_file || "";
  }
  if (projectSelectedFile && (path || project.project_file)) {
    projectSelectedFile.removeAttribute("data-i18n");
    projectSelectedFile.textContent = shortPath(path || project.project_file || "");
  }
  if (project.dataset_config) {
    forms.dataset.elements.config.value = project.dataset_config;
    activeDataset = {
      code: project.dataset_code || "RESTORED-DATASET",
      config: project.dataset_config,
      locked_at: project.updated_at || new Date().toISOString(),
    };
    localStorage.setItem("spectramatrix_active_dataset", JSON.stringify(activeDataset));
  }
  if (project.matrix_config) {
    forms.matrix.elements.config.value = project.matrix_config;
  }
  if (project.training_design) {
    applyTrainingDesignState(project.training_design);
  }
  if (project.matrix_out) {
    forms.matrix.elements.out.value = project.matrix_out;
  }
  if (project.tasks_dir) {
    forms.queue.elements.tasks.value = project.tasks_dir;
    forms.monitor.elements.tasks.value = project.tasks_dir;
    forms.scan.elements.runs.value = project.tasks_dir;
  }
  if (project.registry) {
    forms.candidate.elements.registry.value = project.registry;
    forms.aggregate.elements.registry.value = project.registry;
  }
  selectedOutputTaskId = project.selected_output_task_id || "";
  activeQueueJobId = project.queue_job_id || "";
  workspaceState = {
    ...workspaceState,
    projectPath: path || project.project_file || "",
    datasetCode: project.dataset_code || "",
    datasetConfig: project.dataset_config || "",
    importManifest: project.import_manifest || "",
    trainingDesign: project.training_design || null,
    workshopDesign: project.workshop_design || null,
    matrixDir: project.matrix_dir || "",
    taskIndex: project.task_index || "",
    matrixManifest: project.manifest || "",
    tasksDir: project.tasks_dir || "",
    registry: project.registry || "",
    selectedOutputTaskId: project.selected_output_task_id || "",
    queueJobId: project.queue_job_id || "",
    queueStatus: project.queue_status || "",
    queueResult: project.queue_result || null,
    outputs: project.outputs || null,
    updatedAt: new Date().toISOString(),
  };
  localStorage.setItem("spectramatrix_workspace_state", JSON.stringify(workspaceState));
  applyWorkshopDesignState(project.workshop_design || workspaceState.workshopDesign || null);
  renderActiveDataset();
  renderResultSelectionState();
  if (project.dataset_config) {
    await inspectDataset({ manual: false, silent: true });
  }
  if (project.tasks_dir) {
    await refreshTasks({ silent: true });
  }
  if (project.registry) {
    await renderModelOutputsFromRegistry(project.registry, { silent: true, taskId: selectedOutputTaskId });
  }
}

function setProjectStatus(text, state) {
  if (!projectStatus) {
    return;
  }
  projectStatus.removeAttribute("data-i18n");
  projectStatus.textContent = text;
  projectStatus.className = `project-status ${state || ""}`.trim();
}

async function restoreWorkspaceState() {
  if (!workspaceState || typeof workspaceState !== "object") {
    return;
  }
  if (workspaceState.datasetConfig) {
    forms.dataset.elements.config.value = workspaceState.datasetConfig;
    forms.matrix.elements.config.value = forms.matrix.elements.config.value || "";
    if (!activeDataset || !activeDataset.config) {
      activeDataset = {
        code: workspaceState.datasetCode || "RESTORED-DATASET",
        config: workspaceState.datasetConfig,
        locked_at: workspaceState.updatedAt || new Date().toISOString(),
      };
      localStorage.setItem("spectramatrix_active_dataset", JSON.stringify(activeDataset));
    }
    await inspectDataset({ manual: false, silent: true });
  }
  if (projectFilePath && workspaceState.projectPath) {
    projectFilePath.value = workspaceState.projectPath;
  }
  if (workspaceState.trainingDesign) {
    applyTrainingDesignState(workspaceState.trainingDesign);
  }
  applyWorkshopDesignState(workspaceState.workshopDesign || null);
  if (workspaceState.tasksDir) {
    forms.queue.elements.tasks.value = workspaceState.tasksDir;
    forms.monitor.elements.tasks.value = workspaceState.tasksDir;
    forms.scan.elements.runs.value = workspaceState.tasksDir;
    await refreshTasks({ silent: true });
  }
  if (workspaceState.registry) {
    forms.candidate.elements.registry.value = workspaceState.registry;
    forms.aggregate.elements.registry.value = workspaceState.registry;
    selectedOutputTaskId = workspaceState.selectedOutputTaskId || "";
    await renderModelOutputsFromRegistry(workspaceState.registry, { silent: true, taskId: selectedOutputTaskId });
  }
  renderActiveDataset();
  renderResultSelectionState();
}

async function refreshTasks(options = {}) {
  const payload = formPayload(forms.monitor);
  try {
    const data = await fetchJson("/api/tasks/list", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderTaskTable(data);
    if (!options.silent) {
      appendResult("Task refresh", "ok", `tasks=${data.total}, folder=${data.tasks_dir}`, data);
    }
  } catch (error) {
    renderTaskError(error.message);
    if (!options.silent) {
      appendResult("Task refresh", "fail", error.message, { error: error.message, payload });
    }
  }
}

async function loadTaskLog(taskDir) {
  try {
    const data = await fetchJson("/api/tasks/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task_dir: taskDir,
        log: taskLogKind.value,
        max_chars: 12000,
      }),
    });
    taskLogKind.dataset.taskDir = taskDir;
    taskLogPath.textContent = data.exists ? data.path : `${data.path} not found`;
    taskLogOutput.textContent = data.content || "(empty)";
  } catch (error) {
    taskLogPath.textContent = error.message;
    taskLogOutput.textContent = "";
  }
}

async function handleMatrixCreated(data, options = {}) {
  if (!data.tasks_dir) {
    return;
  }
  forms.queue.elements.tasks.value = data.tasks_dir;
  forms.monitor.elements.tasks.value = data.tasks_dir;
  forms.scan.elements.runs.value = data.tasks_dir;
  if (projectFilePath && data.matrix_dir) {
    projectFilePath.value = `${data.matrix_dir.replace(/\/$/, "")}/SpectraMatrix_Project.spectramatrix.json`;
  }
  saveWorkspaceState({
    projectPath: projectFilePath ? projectFilePath.value.trim() : "",
    matrixDir: data.matrix_dir || "",
    tasksDir: data.tasks_dir,
    taskCount: data.task_count || 0,
    taskIndex: data.task_index || "",
    matrixManifest: data.manifest || "",
  });
  const count = Number(data.task_count || 0);
  const title = options.exportOnly ? t("matrix.exportedTitle") : t("matrix.createdTitle");
  setMatrixStatus(`${title}：${count}`, "ok");
  matrixResult.hidden = false;
  matrixResultTitle.textContent = `${title}：${count}`;
  matrixResultDetail.textContent = `${t("matrix.createdDetail")} ${shortPath(data.tasks_dir)}`;
  try {
    const taskData = await fetchJson("/api/tasks/list", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tasks: data.tasks_dir }),
    });
    renderTaskTable(taskData);
    renderMatrixCreatedTaskBlocks(taskData.rows || [], taskData.total || 0);
  } catch (error) {
    renderMatrixCreatedTaskBlocks([], 0, error.message);
  }
}

function renderMatrixCreatedTaskBlocks(rows, total, error = "") {
  if (!matrixCreatedTaskBlocks) {
    return;
  }
  if (error) {
    matrixCreatedTaskBlocks.innerHTML = `<p class="empty-hint">${escapeHtml(error)}</p>`;
    return;
  }
  if (!rows.length) {
    matrixCreatedTaskBlocks.innerHTML = `<p class="empty-hint">${t("monitor.empty")}</p>`;
    return;
  }
  const visible = rows.slice(0, 80);
  const overflow = total > visible.length
    ? `<p class="empty-hint">${currentLanguage === "zh" ? `已显示前 ${visible.length} 个任务，共 ${total} 个。` : `Showing first ${visible.length} of ${total} tasks.`}</p>`
    : "";
  matrixCreatedTaskBlocks.innerHTML = visible.map((row, index) => renderTaskBlock(row, index)).join("") + overflow;
}

function updateDatasetCards(data) {
  document.querySelector("#metric-samples").textContent = data.samples ?? "--";
  document.querySelector("#metric-wavelengths").textContent = data.wavelengths ?? "--";
  document.querySelector("#metric-windows").textContent = data.window_count ?? "--";
  document.querySelector("#metric-targets").textContent = targetCount(data.target_columns);
}

function renderTaskTable(data) {
  const counts = data.counts || {};
  taskSummary.textContent = currentLanguage === "zh" ? `${data.total} 个任务` : `${data.total} tasks`;
  taskSummary.title = data.tasks_dir;
  taskCounts.innerHTML = Object.keys(counts)
    .sort()
    .map((key) => `<span class="count-chip">${escapeHtml(displayStatus(key))}: ${escapeHtml(counts[key])}</span>`)
    .join("");
  if (!data.rows || data.rows.length === 0) {
    taskRows.innerHTML = `<tr class="empty-row"><td colspan="8">${t("monitor.empty")}</td></tr>`;
    if (taskBlocks) {
      taskBlocks.innerHTML = `<p class="empty-hint">${t("monitor.empty")}</p>`;
    }
    return;
  }
  if (taskBlocks) {
    taskBlocks.innerHTML = data.rows.map((row, index) => renderTaskBlock(row, index)).join("");
  }
  taskRows.innerHTML = data.rows
    .map((row, index) => {
      const metric = formatTaskMetric(row);
      const taskLabel = currentLanguage === "zh"
        ? `任务 ${String(index + 1).padStart(3, "0")}`
        : `Task ${String(index + 1).padStart(3, "0")}`;
      const modelLabel = row.model_id
        ? displayParamValue("model_id", row.model_id)
        : displayParamValue("task", row.task);
      const activationLabel = (row.activation || row.activation_id)
        ? displayParamValue("activation_id", row.activation || row.activation_id)
        : "--";
      const augmentationLabel = displayAugmentationSummary(row);
      return `
        <tr>
          <td class="task-id-cell">${escapeHtml(taskLabel)}</td>
          <td><span class="badge status ${statusClass(row.status)}">${escapeHtml(displayStatus(row.status))}</span></td>
          <td>${escapeHtml(row.cv_fold)}</td>
          <td>${escapeHtml(displayParamValue("window_id", row.window_id))}</td>
          <td>${escapeHtml(modelLabel)}</td>
          <td>${escapeHtml(`${activationLabel} · ${augmentationLabel}`)}</td>
          <td class="metric-cell">${escapeHtml(metric)}</td>
          <td><button class="btn btn-sm btn-outline-secondary inline-button" type="button" data-task-dir="${escapeHtml(row.task_dir)}">View</button></td>
        </tr>
      `;
    })
    .join("");
}

function renderTaskError(message) {
  taskSummary.textContent = message;
  taskCounts.innerHTML = "";
  if (taskBlocks) {
    taskBlocks.innerHTML = `<p class="empty-hint">${currentLanguage === "zh" ? "无法加载训练项目。" : "Training project could not be loaded."}</p>`;
  }
  taskRows.innerHTML = `<tr class="empty-row"><td colspan="8">${currentLanguage === "zh" ? "无法加载任务文件夹。" : "Task folder could not be loaded."}</td></tr>`;
}

function renderTaskBlock(row, index) {
  const status = row.status || "pending";
  const metric = formatTaskMetric(row);
  const progress = ["succeeded", "failed", "cancelled"].includes(status) ? 100 : status === "running" ? 50 : 0;
  const taskLabel = currentLanguage === "zh"
    ? `任务 ${String(index + 1).padStart(3, "0")}`
    : `Task ${String(index + 1).padStart(3, "0")}`;
  return `
    <button class="task-block ${statusClass(status)}" type="button" data-task-dir="${escapeHtml(row.task_dir)}">
      <span>${escapeHtml(taskLabel)}</span>
      <strong>${escapeHtml(displayStatus(status))}</strong>
      <i style="--progress:${progress}%"></i>
      <small>${escapeHtml(metric || displayParamValue("task", row.task || "--"))}</small>
      <small>${escapeHtml(displayAugmentationSummary(row))}</small>
    </button>
  `;
}

function displayAugmentationSummary(row) {
  const method = row.augmentation_method || displayParamValue("augmentation_id", row.augmentation_id || "AUG0");
  if ((row.augmentation_id || "AUG0") === "AUG0") {
    return method;
  }
  const multiplier = row.augmentation_multiplier_label || displayParamValue("augmentation_multiplier", row.augmentation_multiplier || 1);
  return `${method} / ${multiplier}`;
}

function formatTaskMetric(row) {
  const name = String(row.metric_name || "");
  if (!name) {
    return "";
  }
  const value = formatMetric(row.metric_value);
  const zh = currentLanguage === "zh";
  const labels = {
    val_rmse: zh ? "验证 RMSE" : "Validation RMSE",
    val_mae: zh ? "验证 MAE" : "Validation MAE",
    val_r2: zh ? "验证 R2" : "Validation R2",
    val_accuracy: zh ? "验证准确率" : "Validation accuracy",
    val_balanced_accuracy: zh ? "验证平衡准确率" : "Validation balanced accuracy",
    val_macro_f1: zh ? "验证 Macro F1" : "Validation macro F1",
    val_f1: zh ? "验证 F1" : "Validation F1",
  };
  const lowerIsBetter = name.includes("rmse") || name.includes("mae") || name.includes("loss");
  const direction = lowerIsBetter
    ? (zh ? "越低越好" : "lower is better")
    : (zh ? "越高越好" : "higher is better");
  return `${labels[name] || name} ${value}（${direction}）`;
}

function statusClass(status) {
  if (status === "succeeded") {
    return "ok";
  }
  if (status === "failed") {
    return "fail";
  }
  if (status === "cancelled") {
    return "cancelled";
  }
  if (status === "running" || status === "stopping") {
    return "running";
  }
  return "pending";
}

function setActiveView(viewName) {
  for (const view of document.querySelectorAll(".view")) {
    view.classList.toggle("active", view.dataset.view === viewName);
  }
  for (const item of document.querySelectorAll("[data-view-target]")) {
    item.classList.toggle("active", item.dataset.viewTarget === viewName);
  }
  history.replaceState(null, "", `#${viewName}`);
}

function applyLanguage() {
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  languageToggle.textContent = currentLanguage === "zh" ? "English" : "中文";
  for (const node of document.querySelectorAll("[data-i18n]")) {
    node.textContent = t(node.dataset.i18n);
  }
  if (forms.matrix.elements.max_tasks) {
    forms.matrix.elements.max_tasks.placeholder = t("matrix.limitPlaceholder");
  }
  if (forms.queue.elements.max_tasks) {
    forms.queue.elements.max_tasks.placeholder = currentLanguage === "zh" ? "留空：跑完所有等待任务" : "Blank: run all pending tasks";
  }
  updateImportPairState();
  renderActiveDataset();
  setQueueJobStatus({ status: queueJobStatus.dataset.status || "idle" });
  renderMatrixPreview(currentMatrixPreview);
  renderFactorialModes();
  rerenderFactorialRows();
  updateTargetRuleVisibility();
  updateSplitModeUi();
  renderDiagnosticsEvents();
  if (workspaceState.outputs) {
    renderModelOutputs(workspaceState.outputs);
  } else {
    renderEmptyModelOutputs();
  }
  renderResultSelectionState();
}

function t(key) {
  return i18n[currentLanguage][key] || i18n.en[key] || key;
}

function formPayload(form) {
  const payload = {};
  for (const element of form.elements) {
    if (!element.name || element.type === "checkbox") {
      continue;
    }
    payload[element.name] = String(element.value).trim();
  }
  return payload;
}

function optionalNumber(value) {
  if (value === "" || value === null || typeof value === "undefined") {
    return null;
  }
  return Number(value);
}

function appendResult(action, status, keyOutput, data) {
  const empty = resultRows.querySelector(".empty-row");
  if (empty) {
    resultRows.innerHTML = "";
  }
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${new Date().toLocaleTimeString()}</td>
    <td>${escapeHtml(action)}</td>
    <td><span class="badge status ${status}">${status}</span></td>
    <td>${escapeHtml(keyOutput)}</td>
  `;
  resultRows.prepend(row);
  jsonOutput.textContent = JSON.stringify(data, null, 2);
  resultSummary.textContent = `${action}: ${status}`;
  recordDiagnosticEvent(action, { status, output: keyOutput, data });
}

function recordDiagnosticEvent(name, detail = {}) {
  const event = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    at: new Date().toISOString(),
    name,
    detail,
  };
  diagnosticsEvents.unshift(event);
  diagnosticsEvents = diagnosticsEvents.slice(0, 80);
  persistDiagnosticsEvents();
  appendDiagnosticsRecordingEvent(event);
  renderDiagnosticsEvents();
}

function persistDiagnosticsEvents() {
  localStorage.setItem("spectramatrix_diagnostics_events", JSON.stringify(diagnosticsEvents));
}

function startDiagnosticsRecording() {
  diagnosticsRecording = {
    active: true,
    session_id: `${Date.now().toString(36)}-${Math.random().toString(16).slice(2, 8)}`,
    started_at: new Date().toISOString(),
    out: logRecorderPath ? logRecorderPath.value.trim() : "",
    events: [],
  };
  persistDiagnosticsRecording();
  recordDiagnosticEvent("diagnostics.recording_started", {
    path: diagnosticsRecording.out,
    url: window.location.href,
  });
  renderDiagnosticsRecorderState();
}

async function stopAndSaveDiagnosticsRecording() {
  if (!diagnosticsRecording || !diagnosticsRecording.active) {
    return;
  }
  recordDiagnosticEvent("diagnostics.recording_stopping", {
    path: logRecorderPath ? logRecorderPath.value.trim() : diagnosticsRecording.out,
  });
  const stoppedAt = new Date().toISOString();
  const payload = {
    out: logRecorderPath ? logRecorderPath.value.trim() : diagnosticsRecording.out,
    session_id: diagnosticsRecording.session_id,
    started_at: diagnosticsRecording.started_at,
    stopped_at: stoppedAt,
    url: window.location.href,
    user_agent: navigator.userAgent,
    events: diagnosticsRecording.events || [],
  };
  setDiagnosticsRecorderMessage(t("logOrb.recording"));
  if (logRecorderStop) {
    logRecorderStop.disabled = true;
  }
  try {
    const data = await fetchJson("/api/diagnostics/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    diagnosticsRecording = {
      active: false,
      session_id: payload.session_id,
      started_at: payload.started_at,
      stopped_at: stoppedAt,
      out: payload.out,
      saved: data,
      events: [],
    };
    persistDiagnosticsRecording();
    recordDiagnosticEvent("diagnostics.saved", data);
    setDiagnosticsRecorderMessage(`${t("logOrb.saved")}：${data.markdown}`);
  } catch (error) {
    if (diagnosticsRecording) {
      diagnosticsRecording.active = true;
      persistDiagnosticsRecording();
    }
    recordDiagnosticEvent("diagnostics.save_failed", { message: error.message, out: payload.out });
    setDiagnosticsRecorderMessage(`${t("logOrb.saveFail")}：${error.message}`);
  } finally {
    renderDiagnosticsRecorderState();
  }
}

function appendDiagnosticsRecordingEvent(event) {
  if (!diagnosticsRecording || !diagnosticsRecording.active) {
    return;
  }
  diagnosticsRecording.events = [...(diagnosticsRecording.events || []), event].slice(-500);
  diagnosticsRecording.out = logRecorderPath ? logRecorderPath.value.trim() : diagnosticsRecording.out;
  persistDiagnosticsRecording();
}

function persistDiagnosticsRecording() {
  if (diagnosticsRecording) {
    localStorage.setItem("spectramatrix_diagnostics_recording", JSON.stringify(diagnosticsRecording));
  } else {
    localStorage.removeItem("spectramatrix_diagnostics_recording");
  }
}

function renderDiagnosticsRecorderState() {
  const active = Boolean(diagnosticsRecording && diagnosticsRecording.active);
  if (logOrbToggle) {
    logOrbToggle.classList.toggle("is-recording", active);
  }
  if (logRecorderStart) {
    logRecorderStart.disabled = active;
  }
  if (logRecorderStop) {
    logRecorderStop.disabled = !active;
  }
  if (logRecorderPath && diagnosticsRecording && diagnosticsRecording.out && !logRecorderPath.value) {
    logRecorderPath.value = diagnosticsRecording.out;
  }
  if (active) {
    const count = diagnosticsRecording.events ? diagnosticsRecording.events.length : 0;
    setDiagnosticsRecorderMessage(`${t("logOrb.recording")} ${count}`);
  } else if (diagnosticsRecording && diagnosticsRecording.saved && diagnosticsRecording.saved.markdown) {
    setDiagnosticsRecorderMessage(`${t("logOrb.saved")}：${diagnosticsRecording.saved.markdown}`);
  } else {
    setDiagnosticsRecorderMessage(t("logOrb.ready"));
  }
}

function setDiagnosticsRecorderMessage(text) {
  if (logRecorderStatus) {
    logRecorderStatus.textContent = text;
    logRecorderStatus.title = text;
  }
}

function renderDiagnosticsEvents() {
  if (!logOrbCount || !logOrbEvents || !logOrbSummary) {
    return;
  }
  logOrbCount.textContent = String(diagnosticsEvents.length);
  logOrbSummary.textContent = diagnosticsEvents.length
    ? `${diagnosticsRecording && diagnosticsRecording.active ? (currentLanguage === "zh" ? "记录中" : "Recording") : (currentLanguage === "zh" ? "最近" : "Latest")} ${diagnosticsEvents.length}`
    : t("logOrb.empty");
  logOrbEvents.innerHTML = diagnosticsEvents.length
    ? diagnosticsEvents.slice(0, 30).map((event) => `
        <li>
          <time>${escapeHtml(new Date(event.at).toLocaleTimeString("zh-CN", { hour12: false }))}</time>
          <code>${escapeHtml(event.name)}</code>
          <span>${escapeHtml(formatDiagnosticDetail(event.detail))}</span>
        </li>
      `).join("")
    : `<li class="is-empty">${escapeHtml(t("logOrb.empty"))}</li>`;
}

function formatDiagnosticDetail(detail) {
  if (!detail || typeof detail !== "object") {
    return String(detail || "");
  }
  if (detail.status || detail.output) {
    return [detail.status, detail.output].filter(Boolean).join(" · ");
  }
  return JSON.stringify(detail).slice(0, 220);
}

async function renderModelOutputsFromRegistry(registry, options = {}) {
  if (!registry) {
    renderEmptyModelOutputs();
    return null;
  }
  const taskId = options.taskId || selectedOutputTaskId || "";
  try {
    const data = await fetchJson("/api/outputs/summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ registry, task_id: taskId || null }),
    });
    selectedOutputTaskId = data.selected_task_id || (data.best && data.best.task_id) || taskId || "";
    renderModelOutputs(data);
    saveWorkspaceState({ registry, outputs: data, selectedOutputTaskId });
    if (!options.silent) {
      appendResult("Model outputs", "ok", summarizeOutput(data), data);
    }
    return data;
  } catch (error) {
    if (!options.silent) {
      appendResult("Model outputs", "fail", error.message, { error: error.message, registry });
    }
    renderOutputNotice(error.message, "fail");
    return null;
  }
}

function renderModelOutputs(data) {
  const best = data.best || {};
  const summary = data.prediction_summary || {};
  if (outputDatasetCode) {
    outputDatasetCode.textContent = activeDataset && activeDataset.code ? activeDataset.code : (workspaceState.datasetCode || "尚未确认");
  }
  if (outputRegistryPath) {
    outputRegistryPath.textContent = shortPath(data.registry || "");
    outputRegistryPath.title = data.registry || "";
  }
  renderOutputModelPicker(data.models || [], (data.best && data.best.task_id) || "");
  if (summary.kind === "regression") {
    outputChartTitle.textContent = t("outputs.regressionPlot");
    outputMetricMainLabel.textContent = "R2";
    outputMetricMain.textContent = formatMetric(summary.r2);
    outputMetricSecondaryLabel.textContent = "RMSE";
    outputMetricSecondary.textContent = formatMetric(summary.rmse);
    outputMetricTertiaryLabel.textContent = "MAE";
    outputMetricTertiary.textContent = formatMetric(summary.mae);
    renderRegressionDots(summary.points || []);
  } else if (summary.kind === "classification") {
    outputChartTitle.textContent = currentLanguage === "zh" ? "分类预测概览" : "Classification Overview";
    outputMetricMainLabel.textContent = currentLanguage === "zh" ? "验证准确率" : "Validation accuracy";
    outputMetricMain.textContent = formatPercent(summary.accuracy);
    outputMetricSecondaryLabel.textContent = best.metric_name || data.metric || "Metric";
    outputMetricSecondary.textContent = formatMetric(best.metric_value);
    outputMetricTertiaryLabel.textContent = currentLanguage === "zh" ? "验证样品" : "Validation samples";
    outputMetricTertiary.textContent = String(summary.n || "--");
    renderClassificationBars(summary.confusion || {});
  } else {
    renderEmptyModelOutputs();
  }
  if (outputDetailList) {
    outputDetailList.innerHTML = `
      <span><strong>${currentLanguage === "zh" ? "当前模型" : "Current model"}</strong>${escapeHtml(best.task_id || "--")}</span>
      <span><strong>${currentLanguage === "zh" ? "任务类型" : "Task"}</strong>${escapeHtml(displayParamValue("task", best.task || "--"))}</span>
      <span><strong>${currentLanguage === "zh" ? "窗口" : "Window"}</strong>${escapeHtml(displayParamValue("window_id", best.window_id || "--"))}</span>
      <span><strong>${currentLanguage === "zh" ? "模型" : "Model"}</strong>${escapeHtml(displayParamValue("model_id", best.model_id || "--"))}</span>
      <span><strong>${currentLanguage === "zh" ? "激活函数" : "Activation"}</strong>${escapeHtml(displayParamValue("activation_id", best.activation || "--"))}</span>
      <span><strong>${currentLanguage === "zh" ? "数据增强" : "Augmentation"}</strong>${escapeHtml(displayAugmentationSummary(best))}</span>
      <span><strong>${currentLanguage === "zh" ? "损失函数" : "Loss"}</strong>${escapeHtml(displayParamValue("loss_id", best.loss_id || "--"))}</span>
      <span><strong>Checkpoint</strong>${escapeHtml(shortPath(best.checkpoint || ""))}</span>
    `;
  }
}

function renderOutputModelPicker(models, activeTaskId) {
  if (!outputModelPicker) {
    return;
  }
  const rows = Array.isArray(models) ? models : [];
  if (!rows.length) {
    outputModelPicker.innerHTML = "";
    return;
  }
  const visibleRows = rows.slice(0, 20);
  const overflow = rows.length > visibleRows.length
    ? `<p class="empty-hint">${currentLanguage === "zh" ? `已显示前 ${visibleRows.length} 个模型，共 ${rows.length} 个。` : `Showing first ${visibleRows.length} of ${rows.length} models.`}</p>`
    : "";
  outputModelPicker.innerHTML = `
    <div class="mini-heading">${escapeHtml(t("outputs.modelPicker"))}</div>
    <div class="output-model-list">
      ${visibleRows.map((row) => {
        const active = row.task_id === activeTaskId;
        const metric = formatTaskMetric(row);
        const title = [
          `#${row.rank}`,
          displayParamValue("model_id", row.model_id || "--"),
          displayParamValue("window_id", row.window_id || "--"),
        ].join(" · ");
        const details = [
          displayParamValue("preprocess_id", row.preprocess_id || "--"),
          displayAugmentationSummary(row),
          displayParamValue("pooling_id", row.pooling_id || "--"),
          displayParamValue("activation_id", row.activation || "--"),
          displayParamValue("loss_id", row.loss_id || "--"),
          row.learning_rate ? `${currentLanguage === "zh" ? "学习率" : "LR"} ${row.learning_rate}` : "",
          row.dropout ? `Dropout ${row.dropout}` : "",
        ].filter(Boolean).join(" / ");
        return `
          <button class="output-model-option${active ? " active" : ""}" type="button" data-output-task-id="${escapeHtml(row.task_id || "")}">
            <strong>${escapeHtml(title)}</strong>
            <span>${escapeHtml(details)}</span>
            <em>${escapeHtml(metric)}</em>
          </button>
        `;
      }).join("")}
    </div>
    ${overflow}
  `;
}

function renderEmptyModelOutputs() {
  if (outputDatasetCode) {
    outputDatasetCode.textContent = activeDataset && activeDataset.code ? activeDataset.code : "尚未确认";
  }
  if (outputRegistryPath) {
    outputRegistryPath.textContent = "尚未生成";
  }
  if (outputMetricMain) outputMetricMain.textContent = "--";
  if (outputMetricSecondary) outputMetricSecondary.textContent = "--";
  if (outputMetricTertiary) outputMetricTertiary.textContent = "--";
  if (outputChartTitle) outputChartTitle.textContent = t("outputs.regressionPlot");
  if (outputChartPoints) outputChartPoints.innerHTML = "";
  if (outputModelPicker) outputModelPicker.innerHTML = "";
  if (outputDetailList) outputDetailList.innerHTML = "";
}

function renderOutputNotice(message, state) {
  if (!outputDetailList) {
    return;
  }
  outputDetailList.innerHTML = `<span class="${escapeHtml(state || "")}"><strong>${currentLanguage === "zh" ? "成果状态" : "Output status"}</strong>${escapeHtml(message)}</span>`;
}

function renderRegressionDots(points) {
  if (!outputChartPoints) {
    return;
  }
  const numeric = points.filter((point) => Number.isFinite(Number(point.true)) && Number.isFinite(Number(point.pred)));
  if (!numeric.length) {
    outputChartPoints.innerHTML = "";
    return;
  }
  const values = numeric.flatMap((point) => [Number(point.true), Number(point.pred)]);
  let min = Math.min(...values);
  let max = Math.max(...values);
  const padding = (max - min || Math.max(1, Math.abs(max))) * 0.08;
  min = Math.max(0, min - padding);
  max = max + padding;
  const span = max > min ? max - min : 1;
  const plot = { left: 17, right: 94, top: 8, bottom: 84 };
  const xFor = (value) => plot.left + ((Number(value) - min) / span) * (plot.right - plot.left);
  const yFor = (value) => plot.bottom - ((Number(value) - min) / span) * (plot.bottom - plot.top);
  const ticks = [min, min + span / 2, max];
  const tickMarkup = ticks.map((value) => {
    const x = xFor(value);
    const y = yFor(value);
    return `
      <line class="chart-grid-line" x1="${plot.left}" x2="${plot.right}" y1="${y.toFixed(2)}" y2="${y.toFixed(2)}"></line>
      <line class="chart-grid-line" x1="${x.toFixed(2)}" x2="${x.toFixed(2)}" y1="${plot.top}" y2="${plot.bottom}"></line>
      <text class="chart-tick x" x="${x.toFixed(2)}" y="91">${escapeHtml(formatAxisTick(value))}</text>
      <text class="chart-tick y" x="14" y="${(y + 1).toFixed(2)}">${escapeHtml(formatAxisTick(value))}</text>
    `;
  }).join("");
  const pointsMarkup = numeric.slice(0, 80).map((point) => `
    <circle
      class="chart-point-svg"
      cx="${xFor(point.true).toFixed(2)}"
      cy="${yFor(point.pred).toFixed(2)}"
      r="1.35"
    ></circle>
  `).join("");
  outputChartPoints.innerHTML = `
    <svg class="regression-svg" viewBox="0 0 100 100" role="img" aria-label="${escapeHtml(t("outputs.regressionPlot"))}">
      ${tickMarkup}
      <line class="chart-axis-line" x1="${plot.left}" x2="${plot.left}" y1="${plot.top}" y2="${plot.bottom}"></line>
      <line class="chart-axis-line" x1="${plot.left}" x2="${plot.right}" y1="${plot.bottom}" y2="${plot.bottom}"></line>
      <line class="chart-reference-line" x1="${xFor(min).toFixed(2)}" y1="${yFor(min).toFixed(2)}" x2="${xFor(max).toFixed(2)}" y2="${yFor(max).toFixed(2)}"></line>
      ${pointsMarkup}
      <text class="chart-label x" x="55" y="98">${currentLanguage === "zh" ? "实测值 PPM" : "Measured PPM"}</text>
      <text class="chart-label y" x="-48" y="5" transform="rotate(-90)">${currentLanguage === "zh" ? "预测值 PPM" : "Predicted PPM"}</text>
    </svg>
  `;
}

function formatAxisTick(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "--";
  }
  if (Math.abs(number) >= 1000) {
    return `${Math.round(number / 100) / 10}k`;
  }
  if (Math.abs(number) >= 100) {
    return String(Math.round(number));
  }
  return number.toFixed(1).replace(/\\.0$/, "");
}

function renderClassificationBars(confusion) {
  if (!outputChartPoints) {
    return;
  }
  const entries = Object.entries(confusion);
  const max = Math.max(1, ...entries.map(([, count]) => Number(count || 0)));
  outputChartPoints.innerHTML = entries.slice(0, 8).map(([label, count]) => {
    const height = 18 + (Number(count || 0) / max) * 62;
    return `<span class="class-bar" style="height:${height.toFixed(1)}%" title="${escapeHtml(label)}: ${escapeHtml(count)}"><b>${escapeHtml(count)}</b></span>`;
  }).join("");
}

function formatMetric(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "--";
  }
  if (Math.abs(number) >= 100) {
    return number.toFixed(1);
  }
  return number.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
}

function formatPercent(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${(number * 100).toFixed(1)}%` : "--";
}

function summarizeOutput(data) {
  if (!data) {
    return "no result yet";
  }
  if (data.job_id) {
    return `job=${data.job_id}, status=${data.status}`;
  }
  if (data.import_id) {
    return summarizeImport(data);
  }
  const keys = ["manifest", "registry", "candidates", "group_summary", "report"];
  for (const key of keys) {
    if (data[key]) {
      return `${key}: ${shortPath(data[key])}`;
    }
  }
  if (typeof data.task_count !== "undefined") {
    return `tasks=${data.task_count}, folder=${shortPath(data.tasks_dir)}`;
  }
  if (typeof data.selected !== "undefined") {
    return `selected=${data.selected}, executed=${data.executed}, dry_run=${data.dry_run}`;
  }
  if (typeof data.total !== "undefined") {
    return `tasks=${data.total}, folder=${shortPath(data.tasks_dir)}`;
  }
  if (typeof data.samples !== "undefined") {
    return `samples=${data.samples}, wavelengths=${data.wavelengths}, windows=${data.window_count}`;
  }
  if (typeof data.selected_rows !== "undefined") {
    return `selected=${data.selected_rows}, metric=${data.metric}`;
  }
  if (typeof data.group_count !== "undefined") {
    return `groups=${data.group_count}, metric=${data.metric}`;
  }
  return "completed";
}

function summarizeImport(data) {
  const count = data.files ? data.files.length : 0;
  const generated = data.generated && data.generated.status === "ready" ? "auto_dataset=yes" : "auto_dataset=no";
  const config = data.dataset_config ? "config=yes" : "config=no";
  return `files=${count}, ${generated}, ${config}`;
}

function setQueueJobStatus(data) {
  if (!queueJobStatus) {
    return;
  }
  if (data.job_id) {
    activeQueueJobId = data.job_id;
  }
  queueJobStatus.dataset.status = data.status || "idle";
  const label = currentLanguage === "zh" ? "训练任务" : "Training job";
  const parts = [`${label}: ${displayStatus(data.status || "idle")}`];
  if (data.job_id) {
    parts.push(`id=${data.job_id}`);
  }
  if (data.request && typeof data.request.dry_run !== "undefined") {
    parts.push(`dry_run=${data.request.dry_run}`);
  }
  if (data.result) {
    parts.push(`selected=${data.result.selected}`);
    parts.push(`executed=${data.result.executed}`);
  }
  if (data.error) {
    parts.push(data.error);
  }
  queueJobStatus.textContent = parts.join(" | ");
  const isActive = ["queued", "starting", "running", "stopping"].includes(data.status || "");
  if (queueStopButton) {
    queueStopButton.disabled = !isActive || (data.status === "stopping");
  }
  if (queueResumeButton) {
    queueResumeButton.disabled = isActive;
  }
}

function setApiState(text, state) {
  apiStatus.textContent = text;
  apiDot.className = `status-dot ${state}`.trim();
}

function shortPath(path) {
  if (!path) {
    return "";
  }
  const parts = String(path).split("/");
  return parts[parts.length - 1] || String(path);
}

function formatBytes(value) {
  const bytes = Number(value || 0);
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function targetCount(value) {
  if (Array.isArray(value)) {
    return value.length;
  }
  if (value && typeof value === "object") {
    return Object.keys(value).length;
  }
  return "--";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

window.addEventListener("error", (event) => {
  recordDiagnosticEvent("window.error", {
    message: event.message,
    source: event.filename,
    line: event.lineno,
  });
});
window.addEventListener("unhandledrejection", (event) => {
  recordDiagnosticEvent("promise.rejection", {
    message: event.reason && event.reason.message ? event.reason.message : String(event.reason || ""),
  });
});

applyLanguage();
updateTargetRuleVisibility();
updateSplitModeUi();
renderDiagnosticsEvents();
renderDiagnosticsRecorderState();
const initialView = location.hash ? location.hash.replace("#", "") : "data";
setActiveView(document.querySelector(`[data-view="${initialView}"]`) ? initialView : "data");
loadDefaults();
