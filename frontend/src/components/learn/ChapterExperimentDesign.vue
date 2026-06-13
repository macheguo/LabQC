<script setup>
</script>

<template>
  <div class="learn-content">
    <h1>第八章：实验设计与报告生成</h1>
    <p class="chapter-subtitle">实验室人员使用 LabQC 的实用指南。</p>

    <!-- ============================================================ -->
    <!-- Section 1: Planning Your QC Program                          -->
    <!-- ============================================================ -->
    <h2>1. 规划您的QC程序</h2>
    <p>
      一个好的QC程序设计始于第一个质控品被测量之前。您在规划阶段所做的决定，决定了您的QC系统是能够
      可靠地检出有临床意义的误差，还是产生掩盖真实问题的噪音。
    </p>

    <h3>需要多少个质控水平？</h3>
    <p>
      每分析批次至少运行<strong>两个质控水平</strong>：一个低值阳性和一个高值阳性。两个水平使您能够
      应用多规则Westgard评估（包括需要两个水平的R-4s规则）。第三个中值水平可改善全报告范围的误差检出，
      建议用于定量检测。
    </p>
    <table>
      <thead>
        <tr>
          <th>质控水平数</th>
          <th>适用场景</th>
          <th>可用的 Westgard 规则</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1 个水平</td>
          <td>仅定性检测</td>
          <td>仅 1-2s、1-3s</td>
        </tr>
        <tr>
          <td>2 个水平（推荐最低要求）</td>
          <td>定量检测</td>
          <td>全部六条规则（1-2s, 1-3s, 2-2s, R-4s, 4-1s, 10x）</td>
        </tr>
        <tr>
          <td>3 个水平</td>
          <td>高样本量的定量检测</td>
          <td>全部规则，全范围内灵敏度增强</td>
        </tr>
      </tbody>
    </table>

    <h3>质控品运行的频次</h3>
    <ul>
      <li><strong>每批次：</strong>当每个分析批次独立产生患者结果时要求（如PCR批次）。</li>
      <li><strong>每班次：</strong>适用于24/7运行的连续分析仪（临床化学、血液学）。</li>
      <li><strong>每批次组：</strong>当患者样本被分成离散的批次组并共用试剂和校准品时。</li>
    </ul>

    <div class="info-box">
      <strong>经验法则：</strong>如有疑问，每批次都运行质控品。质控品的花费与报告错误患者结果的
      代价相比微不足道。
    </div>

    <h3>建立均值和SD</h3>
    <p>
      在应用Westgard规则之前，必须为每个质控水平建立可靠的平均值和标准差估计值。这需要收集
      <strong>至少20个数据点</strong>，在日常操作条件下、跨至少10个不同的批次或日期采集。
    </p>
    <ul>
      <li>在正常条件下与患者样本一同运行质控品——不要使用专门的"调试"批次。</li>
      <li>排除明显的离群值（如失败的提取），但记录每一次排除。</li>
      <li>定期重新计算均值和SD（每6个月或试剂批号变更后）。</li>
    </ul>

    <div class="warning-box">
      <strong>重要：</strong>在拥有至少20个数据点之前，不要应用Westgard规则。规则应用于较少的数据点
      时，将产生不可靠的均值/SD估计值并产生大量假拒绝。
    </div>

    <h3>选择 TEa 值</h3>
    <p>
      允许总误差（TEa）定义了给定分析项目可接受的最大误差。从权威来源选择TEa：
    </p>
    <table>
      <thead>
        <tr>
          <th>来源</th>
          <th>地区/适用范围</th>
          <th>备注</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>CLIA</td>
          <td>美国</td>
          <td>针对受监管分析项目的已发布能力验证标准</td>
        </tr>
        <tr>
          <td>生物学变异数据库</td>
          <td>国际</td>
          <td>由个体内和个体间变异导出的理想TEa</td>
        </tr>
        <tr>
          <td>RILIBAK</td>
          <td>德国</td>
          <td>与目标值的最大允许偏差</td>
        </tr>
        <tr>
          <td>CDSCO / NABL</td>
          <td>印度</td>
          <td>与ISO 15189和制造商规格保持一致</td>
        </tr>
        <tr>
          <td>制造商声明</td>
          <td>全球</td>
          <td>试剂盒说明书中的性能规格（用作最低基线）</td>
        </tr>
      </tbody>
    </table>

    <h3>法规审核所需文件</h3>
    <p>
      您的QC程序文件应包含：
    </p>
    <ul>
      <li>QC策略：应用哪些规则、多少个水平、运行频次。</li>
      <li>均值、SD和TEa值的来源及理由。</li>
      <li>批号变更记录和平行测试数据。</li>
      <li>所有QC失败的纠正措施记录。</li>
      <li>定期进行QC回顾总结（按月或按季度）。</li>
    </ul>

    <!-- ============================================================ -->
    <!-- Section 2: Preparing QC Data Files                           -->
    <!-- ============================================================ -->
    <h2>2. 准备QC数据文件</h2>
    <p>
      LabQC 接受从PCR仪器和临床分析仪导出的Excel（<code>.xlsx</code>）文件。系统支持三种文件格式配置文件：
    </p>

    <h3>支持的格式</h3>
    <table>
      <thead>
        <tr>
          <th>格式</th>
          <th>仪器</th>
          <th>需包含的列</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>QuantStudio</td>
          <td>Applied Biosystems QuantStudio</td>
          <td><code>Sample Name</code>, <code>Target Name</code>, <code>CT</code>, <code>Ct Mean</code>, <code>Ct SD</code></td>
        </tr>
        <tr>
          <td>Bio-Rad CFX</td>
          <td>Bio-Rad CFX96 / CFX384</td>
          <td><code>Sample</code>, <code>Target</code>, <code>Cq</code>, <code>Cq Mean</code>, <code>Cq Std. Dev</code></td>
        </tr>
        <tr>
          <td>通用</td>
          <td>任意仪器</td>
          <td>用户自定义列映射（样本、目标、数值列）</td>
        </tr>
      </tbody>
    </table>

    <h3>如何从常用仪器导出数据</h3>

    <p><strong>Applied Biosystems QuantStudio：</strong></p>
    <ol>
      <li>在 QuantStudio Design &amp; Analysis 软件中打开实验。</li>
      <li>进入 <strong>Export</strong> &gt; <strong>Results</strong>。</li>
      <li>选择 <code>.xlsx</code> 格式并保存。</li>
      <li>导出的文件可直接以 QuantStudio 格式在 LabQC 中使用。</li>
    </ol>

    <p><strong>Bio-Rad CFX Manager：</strong></p>
    <ol>
      <li>在 CFX Manager 中打开该次运行。</li>
      <li>进入 <strong>Export</strong> &gt; <strong>Quantification Cq Results</strong>。</li>
      <li>保存为 <code>.xlsx</code>。</li>
      <li>在 LabQC 中使用 Bio-Rad CFX 格式。</li>
    </ol>

    <p><strong>Roche LightCycler：</strong></p>
    <ol>
      <li>从 LightCycler 软件中导出分析结果为 <code>.xlsx</code>。</li>
      <li>在 LabQC 中使用<strong>通用格式</strong>，手动映射列（样本名称、目标、Ct/Cp值）。</li>
    </ol>

    <p><strong>临床化学分析仪：</strong></p>
    <ol>
      <li>从分析仪软件或LIS导出每日QC报告为 <code>.xlsx</code>。</li>
      <li>确保文件包含样本标识、分析项目名称和测量值列。</li>
      <li>使用通用格式和适当的列映射。</li>
    </ol>

    <p><strong>血液学分析仪：</strong></p>
    <ol>
      <li>从分析仪软件导出QC数据为 <code>.xlsx</code>。</li>
      <li>确保文件包含质控水平、参数名称和测量值列。</li>
      <li>使用通用格式和列映射。</li>
    </ol>

    <h3>通用格式的列映射</h3>
    <p>
      使用通用格式时，您需指定文件中哪些列对应所需字段。LabQC 会读取您的列标题，允许您进行映射：
    </p>
    <ul>
      <li><strong>样本列：</strong>包含样本或质控品标识符的列。</li>
      <li><strong>目标列：</strong>包含分析项目或目标名称的列。</li>
      <li><strong>数值列：</strong>包含测量值（Ct、浓度、计数等）的列。</li>
    </ul>

    <h3>数据文件最佳实践</h3>
    <ul>
      <li><strong>命名一致：</strong>在所有文件中使用相同的样本名称和目标名称（如始终用"QC-Low"，而非有时用"QC Low"或"qc_low"）。</li>
      <li><strong>包含批号：</strong>在上传时记录试剂和质控品批号至元数据字段。</li>
      <li><strong>记录日期：</strong>确保导出的文件包含运行日期信息，或在上传时手动输入日期。</li>
      <li><strong>不要修改导出文件：</strong>上传仪器导出的原始文件。人为编辑可能引入错误并破坏审计追踪的完整性。</li>
    </ul>

    <div class="info-box">
      <strong>提示：</strong>在上传自有数据之前，先用 <code>example_sets/</code> 目录中的示例数据集
      熟悉预期的文件格式。文件如 <code>sample_qc_quantstudio.xlsx</code> 和 <code>sample_qc_biorad.xlsx</code>
      展示了正确的列结构。
    </div>

    <!-- ============================================================ -->
    <!-- Section 3: Setting Up Lot Tracking                           -->
    <!-- ============================================================ -->
    <h2>3. 设置批号追踪</h2>
    <p>
      试剂和质控品批号是实验室测量结果变异的主要来源之一。新批号的质控品可能与上一批号有不同的
      目标值（均值）和离散度（SD），即便它们来自同一制造商和目录编号。
    </p>

    <h3>批号追踪为何重要</h3>
    <ul>
      <li>新批号可能使均值Ct或浓度偏移，若仍使用旧的均值/SD会引发假的Westgard违例。</li>
      <li>法规标准要求结果可追溯至具体的试剂和质控品批号。</li>
      <li>批号追踪可在QC失败时进行根本原因分析——是批号变更还是真实的分析误差？</li>
    </ul>

    <h3>何时注册新批号</h3>
    <p>
      每当您收到带有不同批号的新质控品或试剂盒时，在新批号<em>首次使用之前</em>，
      在<strong>批号管理</strong>中注册。
    </p>

    <h3>如何处理批号切换</h3>
    <ol>
      <li>在批号管理中将<strong>新批号注册</strong>，包括批号编号、制造商、物料类型和有效期。</li>
      <li>新批号与旧批号<strong>平行运行</strong>至少5次（理想情况下20次以建立完整的均值/SD）。</li>
      <li>从平行数据中<strong>建立新批号的均值和SD</strong>。</li>
      <li><strong>切换</strong>至新批号，并在 LabQC 中标记批号变更。</li>
      <li><strong>记录此次过渡</strong>，包括平行测试结果和切换日期。</li>
    </ol>

    <div class="info-box">
      <strong>LabQC行为说明：</strong>LabQC 在批号边界自动重置Westgard规则评估历史。这可以
      防止前一批号数据的遗留违例影响新批号的评估。旧批号的历史数据保留以供审阅。
    </div>

    <!-- ============================================================ -->
    <!-- Section 4: Running QC Analysis — Step by Step                -->
    <!-- ============================================================ -->
    <h2>4. 运行 QC 分析 —— 逐步操作</h2>

    <h3>用于 RT-PCR / 分子检测</h3>
    <ol>
      <li>从仪器软件（QuantStudio、CFX Manager等）中导出QC数据为 <code>.xlsx</code> 格式。</li>
      <li>在 LabQC 中打开 <strong>QC 监测</strong>。</li>
      <li>点击上传区域或将文件拖放至该区域上传文件。</li>
      <li>输入元数据：仪器名称、检测项目名称、荧光通道、试剂批号、质控品批号。</li>
      <li>点击<strong>上传并分析</strong>。</li>
      <li>查阅 Levey-Jennings 图——观察趋势、偏移和离群值。</li>
      <li>检查违例表中是否有任何 Westgard 规则违例。</li>
      <li>做出决定：接受批次并报告患者结果，或调查违例后再发布结果。</li>
    </ol>

    <h3>用于临床化学</h3>
    <p>
      工作流程与上述RT-PCR流程相同。需注意，在LabQC中，界面中标注为"Ct值"的数值字段在临床化学分析
      项目中代表测量浓度或活性值。Westgard评估和Levey-Jennings图绘制的工作方式不变，无论该数值
      代表Ct值、以 mg/dL 计的浓度还是以 U/L 计的酶活性。
    </p>

    <h3>用于血液学</h3>
    <p>
      同样适用上述工作流程。从血液学分析仪导出QC数据，使用通用格式上传，将各列映射至CBC参数
      （WBC、RBC、Hgb、Hct、PLT等）。每个参数被作为一个独立的质控水平进行追踪。
    </p>

    <div class="warning-box">
      <strong>请记住：</strong>除了检查规则违例外，始终目视审阅 Levey-Jennings 图。统计规则
      可能漏掉有经验的人员能看出的细微趋势，而目视检查提供了纯数字无法传达的上下文信息。
    </div>

    <!-- ============================================================ -->
    <!-- Section 5: Performing Sigma Analysis                         -->
    <!-- ============================================================ -->
    <h2>5. 执行 Sigma 分析</h2>
    <p>
      Sigma 分析通过将允许误差（TEa）、系统误差（偏倚）和随机误差（不精密度/CV）组合为单一指标，
      来量化分析方法的质量。Sigma值越高，方法越稳健，容错裕度越大。
    </p>

    <h3>在哪里找到 TEa 值</h3>
    <table>
      <thead>
        <tr>
          <th>来源</th>
          <th>适用范围</th>
          <th>获取途径</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>CLIA</td>
          <td>美国实验室</td>
          <td>发布于 42 CFR 493, Subpart I — 能力验证项目</td>
        </tr>
        <tr>
          <td>RILIBAK</td>
          <td>德国实验室</td>
          <td>由德国医学会（Bundesärztekammer）发布</td>
        </tr>
        <tr>
          <td>生物学变异数据库</td>
          <td>国际（理想TEa）</td>
          <td>EFLM 生物学变异数据库（biologicalvariation.eu）</td>
        </tr>
        <tr>
          <td>CDSCO / NABL</td>
          <td>印度实验室</td>
          <td>与 ISO 15189 一致的 NABL 指南</td>
        </tr>
        <tr>
          <td>制造商说明书</td>
          <td>全球（作为基线）</td>
          <td>IVD试剂盒说明书中的性能规格部分</td>
        </tr>
      </tbody>
    </table>

    <h3>如何计算偏倚</h3>
    <p>
      偏倚是您方法的结果与真实（或公认参考）值之间的系统性差异。有以下几种方法：
    </p>
    <ul>
      <li>
        <strong>通过EQA/PT计划结果：</strong>将您实验室的结果与外部质量评估或能力验证计划中的
        同组均值进行比较。偏倚 = (您的均值 &minus; 同组均值) / 同组均值 &times; 100%。
      </li>
      <li>
        <strong>通过同组比较：</strong>如果您的仪器参与了制造商同组比对，使用您的结果与组内
        共识值之间的差异。
      </li>
      <li>
        <strong>通过回收实验：</strong>将已知数量的分析物加入样本基质中，测量回收量。
        偏倚 = (回收量 &minus; 加入量) / 加入量 &times; 100%。
      </li>
    </ul>

    <h3>如何计算 CV</h3>
    <p>
      CV（变异系数）量化了方法的不精密度：
    </p>
    <ul>
      <li>
        <strong>来自您自己的QC数据：</strong>使用至少20个常规QC批次的数据点。
        CV = (SD / 均值) &times; 100%。Sigma 计算应使用批间（再现性）CV，因为它反映了
        总的方法变异。
      </li>
      <li>
        <strong>使用 LabQC 的精密度模块：</strong>上传您的精密度研究数据，LabQC 将自动
        计算批内和批间CV。
      </li>
    </ul>

    <h3>输入数值并解读 NMEDx 图</h3>
    <p>
      在<strong>Sigma 分析</strong>模块中，输入每个检测项目的TEa、偏倚和CV。点击计算后，查阅：
    </p>
    <ul>
      <li><strong>Sigma值：</strong>以 (TEa &minus; |偏倚|) / CV 计算得出。</li>
      <li><strong>性能分级：</strong>世界级(&ge;6)、优秀(5&ndash;6)、良好(4&ndash;5)、临界(3&ndash;4)、差(2&ndash;3)或不可接受(&lt;2)。</li>
      <li><strong>NMEDx图：</strong>您的检测项目以偏倚为y轴、不精密度为x轴绘制，两者均归一化至TEa。着色区域显示您方法的裕度大小。</li>
    </ul>

    <div class="info-box">
      <strong>解读：</strong>绘于NMEDx图绿色/蓝色区域的检测项目具有充足的裕度——简单的QC规则搭配
      两个质控品已足够。绘于黄色或红色区域的项目则需要更严格的QC规则、每批次更多的质控品数量，
      或是方法的改进。
    </div>

    <!-- ============================================================ -->
    <!-- Section 6: Method Validation Workflow                        -->
    <!-- ============================================================ -->
    <h2>6. 方法验证工作流程</h2>
    <p>
      当引入新方法、启用新仪器或切换新试剂配方时，均需要进行方法验证。其目标是在您的实验室和
      常规操作条件下，证明该方法的表现是可接受的。
    </p>

    <h3>LOD 研究设计</h3>
    <ul>
      <li>准备 <strong>20个空白样本的重复</strong>（不含目标分析物）。</li>
      <li>在预期LOD附近准备 <strong>3&ndash;5 个浓度水平各20个重复</strong>。</li>
      <li>在同一天、相同条件下运行所有重复。</li>
      <li>记录：浓度、复孔号、测量值（Ct或信号）。</li>
    </ul>
    <pre class="diagram">
  LOD 研究布局：

  浓度           重复数      预期结果
  -------------------------------------------------------
  空白 (0)       20         无检出（基线）
  0.5x LOD       20         部分检出
  1x LOD         20         >= 95% 检出
  2x LOD         20         ~100% 检出
  5x LOD         20         100% 检出

  LOD = 在 >= 95% 的重复中被检出的最低浓度
    </pre>

    <h3>LOQ 研究设计</h3>
    <ul>
      <li>准备 <strong>5&ndash;7 个浓度各10个重复</strong>。</li>
      <li>浓度应覆盖从LOD至约10&times; LOD的范围。</li>
      <li>计算每个浓度水平的CV。</li>
      <li>LOQ = CV &le; 阈值（通常20%）的最低浓度。</li>
    </ul>
    <pre class="diagram">
  LOQ 研究布局：

  浓度           重复数      CV 计算值      是否通过？
  -----------------------------------------------------------
  1x LOD         10          35%            否
  2x LOD         10          25%            否
  3x LOD         10          18%            是 (LOQ)
  5x LOD         10          12%            是
  7x LOD         10          8%             是
  10x LOD        10          5%             是

  在此示例中 LOQ = 3x LOD （CV <= 20% 的首个水平）
    </pre>

    <h3>精密度研究设计</h3>
    <p>
      精密度从两个层面进行评估：
    </p>
    <ul>
      <li>
        <strong>批内（重复性）：</strong>在单分析批内对同一样品运行20个重复。
        至少使用2个浓度水平（低和高）。
      </li>
      <li>
        <strong>批间（再现性）：</strong>在至少3天中运行最少3个批次，每个浓度水平
        每批至少 2&ndash;3 个重复。
      </li>
      <li>记录：运行日期、批号、复孔号、测量值。</li>
    </ul>
    <pre class="diagram">
  精密度研究布局：

  批内（单批，同一天）：
  水平        重复数       计算
  ----------------------------------
  低          20           均值、SD、CV
  高          20           均值、SD、CV

  批间（跨天数）：
  水平        批次数   天数    每批复孔数     计算
  -------------------------------------------------------
  低          >= 3    >= 3    2-3              均值、SD、CV（总）
  高          >= 3    >= 3    2-3              均值、SD、CV（总）
    </pre>

    <h3>线性研究设计</h3>
    <ul>
      <li>准备 <strong>5&ndash;7 个浓度水平</strong>覆盖可报告范围。</li>
      <li>每个水平至少运行 <strong>3 个重复</strong>。</li>
      <li>包含预期测量范围的最低值和最高值。</li>
      <li>记录：预期浓度、测量值、复孔号。</li>
    </ul>
    <pre class="diagram">
  线性研究布局：

  水平    预期浓度           重复数    测量值
  ---------------------------------------------------------
  1       10 copies/mL       3         Ct1, Ct2, Ct3
  2       100 copies/mL      3         Ct1, Ct2, Ct3
  3       1,000 copies/mL    3         Ct1, Ct2, Ct3
  4       10,000 copies/mL   3         Ct1, Ct2, Ct3
  5       100,000 copies/mL  3         Ct1, Ct2, Ct3
  6       1,000,000 c/mL     3         Ct1, Ct2, Ct3

  评估: R² >= 0.99, 斜率在 -3.1 至 -3.6 之间
    </pre>

    <div class="info-box">
      <strong>LabQC提示：</strong>将验证研究数据上传至<strong>方法验证</strong>模块。
      选择研究类型（LOD、精密度或线性），定义接受标准，LabQC 将执行统计分析并生成适合
      法规提交的验证报告。
    </div>

    <!-- ============================================================ -->
    <!-- Section 7: Generating Reports                                -->
    <!-- ============================================================ -->
    <h2>7. 生成报告</h2>
    <p>
      LabQC 提供多种报告类型，以支持日常QC审查、管理回顾和法规合规。
    </p>

    <h3>QC 批次报告</h3>
    <p>
      在 QC 监测中每次QC分析后生成。包含：
    </p>
    <ul>
      <li>每个质控水平的汇总统计（均值、SD、CV）。</li>
      <li>含所有数据点和SD线的 Levey-Jennings 图。</li>
      <li>完整的Westgard规则违例清单及严重程度分级。</li>
      <li>批次元数据：仪器、检测项目、通道、试剂批号、质控品批号、日期/时间。</li>
      <li>审计追踪引用（哈希和时间戳）。</li>
    </ul>
    <p>
      <strong>何时生成：</strong>每次QC分析后，尤其是检出违例时。将报告与原始数据文件一同归档。
    </p>

    <h3>Sigma 报告</h3>
    <p>
      从 Sigma 分析模块生成。包含：
    </p>
    <ul>
      <li>每个检测项目的TEa、偏倚和CV值。</li>
      <li>计算出的 Sigma 值和性能分级。</li>
      <li>NMEDx 图可视化。</li>
      <li>推荐的QC规则和质控品数量。</li>
    </ul>
    <p>
      <strong>何时生成：</strong>在QC规划会议、管理回顾期间，以及评估是否需要变更QC策略时。
    </p>

    <h3>验证报告</h3>
    <p>
      完成验证研究后从验证模块生成。包含：
    </p>
    <ul>
      <li>研究类型、接受标准和研究设计参数。</li>
      <li>原始数据摘要和计算的统计量（LOD、CV、R<sup>2</sup>、斜率）。</li>
      <li>每条接受标准的合格/不合格判定。</li>
      <li>可视化图表（散点图、分布图）。</li>
    </ul>
    <p>
      <strong>何时生成：</strong>每项验证研究结束时，纳入方法验证文件包供法规提交使用。
    </p>

    <h3>审计追踪导出</h3>
    <p>
      从审计追踪视图生成。包含：
    </p>
    <ul>
      <li>所有系统操作的时间顺序记录（上传、分析、导出、批号变更、配置变更）。</li>
      <li>每个条目的时间戳、用户标识和操作详情。</li>
      <li>哈希链完整性状态。</li>
    </ul>
    <p>
      <strong>何时生成：</strong>法规检查之前、认可审核期间，以及作为月度备份实践。
    </p>

    <h3>报告最佳实践</h3>
    <ul>
      <li><strong>分析完成后立即生成报告。</strong>不要拖延——数据最新鲜、上下文最清晰的时候就是运行刚结束时。</li>
      <li><strong>将PDF报告与原始数据一同归档。</strong>将原始的 <code>.xlsx</code> 文件和生成的报告存储在
        同一目录或文档管理系统中。</li>
      <li><strong>每月导出审计追踪</strong>作为备份。这在系统故障时提供了独立副本。</li>
      <li><strong>在报告中对批号变更进行说明。</strong>当批号切换发生时，将平行测试数据和新的均值/SD计算结果
        附至QC报告中。</li>
    </ul>

    <!-- ============================================================ -->
    <!-- Section 8: Maintaining Audit Trail Integrity                 -->
    <!-- ============================================================ -->
    <h2>8. 维护审计追踪完整性</h2>
    <p>
      审计追踪是您实验室证明数据未被事后篡改的证据。LabQC 使用SHA-256哈希链确保每条操作被不可篡改地、
      按顺序地记录。
    </p>

    <h3>自动记录的内容</h3>
    <ul>
      <li>文件上传（含文件名、文件哈希和文件大小）。</li>
      <li>QC分析（所用参数、计算结果）。</li>
      <li>报告导出（报告类型、格式、时间戳）。</li>
      <li>批号变更（旧批号、新批号、生效日期）。</li>
      <li>配置变更（被修改的设置项、旧值、新值）。</li>
    </ul>

    <h3>链完整性如何运作</h3>
    <p>
      每个审计条目使用SHA-256进行哈希处理，且每个哈希都包含前一条条目的哈希值。这创建了一条
      不可打破的链条：修改任何单一条目都会使所有后续哈希失效，篡改立即被检出。
    </p>

    <h3>如何验证链完整性</h3>
    <ol>
      <li>进入<strong>审计追踪</strong>视图。</li>
      <li>点击<strong>验证链条</strong>（或"验证完整性"）。</li>
      <li>LabQC 从头开始重新计算链条中每条哈希，并与存储的哈希值比对。</li>
      <li>绿色确认表示链条完整。红色警告标识出链条断裂的确切条目。</li>
    </ol>

    <h3>若检出篡改应如何应对</h3>
    <ol>
      <li>立即记录发现结果，包括条目编号、时间戳和异常的性质。</li>
      <li>通知您的质量负责人和IT管理员。</li>
      <li>调查根本原因：是故意篡改、软件缺陷还是数据损坏？</li>
      <li>复核受影响时间段内关联的所有患者结果。</li>
      <li>将调查发现和纠正措施记录在质量管理体系中。</li>
    </ol>

    <div class="warning-box">
      <strong>法规义务：</strong>根据ISO 15189、21 CFR Part 11及同等标准，任何被发现的数据
      完整性故障都必须进行调查和记录。对篡改检测发现不作为，本身就是一项合规违规。
    </div>

    <h3>审计追踪最佳实践</h3>
    <ul>
      <li><strong>上传后绝不修改Excel文件。</strong>如需修正，上传新的修正文件——原始件和修正件都会被记录。</li>
      <li><strong>所有批号变更都通过批号管理进行。</strong>通过注册表进行的变更会自动记录在审计追踪中。</li>
      <li><strong>系统维护前导出审计追踪。</strong>这保留了一份基线，以防维护过程影响数据。</li>
      <li><strong>保留文件哈希供外部核验。</strong>将上传文件的SHA-256哈希记录在独立系统（如实验记录本或LIMS）中，以便交叉核验。</li>
    </ul>

    <!-- ============================================================ -->
    <!-- Section 9: Troubleshooting Common Issues                     -->
    <!-- ============================================================ -->
    <h2>9. 常见问题排查</h2>

    <table>
      <thead>
        <tr>
          <th>问题</th>
          <th>可能原因</th>
          <th>解决方案</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>"无均值/SD" 报错</td>
          <td>上传的文件未包含Ct Mean/SD列，或未分配具有已有值的质控品批号。</td>
          <td>确保导出的文件包含均值和SD列，或在批号管理中分配一个已有至少20个数据点建立的均值/SD值的质控品批号。</td>
        </tr>
        <tr>
          <td>最初几次运行即出现Westgard违例</td>
          <td>历史数据点不足，无法建立可靠的均值和SD。</td>
          <td>在应用Westgard规则前收集至少20个数据点。初始运行仅用于建立基线统计量。</td>
        </tr>
        <tr>
          <td>R-4s 意外触发</td>
          <td>两个质控水平可能未包含在同一批次中，或水平间存在真实的离散。</td>
          <td>核实每次上传的文件中均包含两个质控水平（L1和L2）。若发散为真实情况，则调查分析过程。</td>
        </tr>
        <tr>
          <td>验证的 LOD 似乎偏高</td>
          <td>空白污染或重复次数不足导致基线升高。</td>
          <td>检查空白样本是否受污染。增加重复数量（使用20次或更多）。确保样本基质具有代表性。</td>
        </tr>
        <tr>
          <td>Sigma 值为"不可接受"</td>
          <td>方法的偏倚和/或不精密度超出TEa所允许的范围。</td>
          <td>复核方法偏倚（考虑重新校准或更换校准品）。复核精密度（检查维护、试剂质量）。若方法从根本上无法满足TEa要求，考虑更换为性能更好的方法或平台。</td>
        </tr>
      </tbody>
    </table>

    <div class="info-box">
      <strong>通用排查提示：</strong>当遇到意外结果时，始终先检查基本情况：文件格式是否正确、
      列名是否正确、数据点是否充足、批号分配是否正确。大多数问题是由数据准备错误而非分析问题引起的。
    </div>
  </div>
</template>
