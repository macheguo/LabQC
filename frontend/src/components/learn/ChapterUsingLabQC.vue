<script setup>
</script>

<template>
  <div class="learn-content">
    <h1>第六章：使用 LabQC —— 逐步指南</h1>
    <p class="chapter-subtitle">软件各模块的详细操作指南。</p>

    <h2>QC 监测模块使用指南</h2>
    <p>
      QC 监测是 LabQC 的核心模块。它接收原始QC数据文件，执行Westgard规则评估，
      生成Levey-Jennings图并输出QC报告。
    </p>

    <h3>步骤1：上传 Excel 文件</h3>
    <p>
      从侧栏进入 <strong>QC 监测</strong>。页面顶部显示文件上传区域。
    </p>
    <ul>
      <li>点击上传区域或将文件拖放至该区域。</li>
      <li><strong>支持的格式：</strong>从QuantStudio、Bio-Rad CFX、Roche LightCycler等PCR仪器
        导出的 <code>.xlsx</code>（Excel）文件。</li>
      <li>文件必须包含样本标识列和Ct值列。LabQC 会自动识别常见的列命名规范。</li>
      <li><strong>可试用的示例文件：</strong>示例数据目录中的 <code>sample_qc_quantstudio.xlsx</code>。</li>
    </ul>

    <h3>步骤2：填写元数据</h3>
    <p>
      选择文件后，填写元数据字段：
    </p>
    <ul>
      <li><strong>仪器：</strong>使用的PCR仪器（如 "QuantStudio 5"、"CFX96"）。这些信息记录在审计追踪中，有助于后续筛选。</li>
      <li><strong>检测项目：</strong>PCR检测名称（如 "SARS-CoV-2 RT-PCR"、"HIV-1 病毒载量"）。</li>
      <li><strong>通道：</strong>荧光通道/报告染料（如 "FAM"、"VIC"、"ROX"）。</li>
      <li><strong>试剂批号：</strong>PCR试剂盒的批号。对追踪批间变异至关重要。</li>
      <li><strong>质控品批号：</strong>QC 质控材料的批号。</li>
    </ul>

    <div class="info-box">
      <strong>提示：</strong>元数据字段为可选项，但强烈建议填写。它们可在仪表盘中实现筛选和分组，
      并包含在QC报告和审计追踪中。
    </div>

    <h3>步骤3：点击上传并分析</h3>
    <p>
      点击上传按钮提交文件。LabQC 将执行以下操作：
    </p>
    <ol>
      <li>解析Excel文件并提取每个质控水平的Ct值。</li>
      <li>从数据中计算汇总统计量（均值、SD、CV）。</li>
      <li>对数据点评估全部六条Westgard规则。</li>
      <li>生成 Levey-Jennings 图。</li>
      <li>在审计追踪中记录本次上传和分析。</li>
    </ol>
    <p>
      分析通常在数秒内完成。进度指示器显示当前状态。
    </p>

    <h3>步骤4：阅读 Levey-Jennings 图</h3>
    <p>
      分析完成后，Levey-Jennings 图显示在上传区域下方。图表展示了：
    </p>
    <ul>
      <li><strong>数据点：</strong>每个圆点代表一次质控测量值，x轴为运行序号，y轴为Ct值。</li>
      <li><strong>中心线：</strong>确认的均值Ct值。</li>
      <li><strong>SD线：</strong>均值±1SD、±2SD和±3SD处的水平线。</li>
      <li><strong>颜色编码：</strong>在可接受限值内的点显示为默认颜色。触发警告或违例的点高亮显示。</li>
    </ul>

    <h3>步骤5：解读违例</h3>
    <p>
      图表下方的违例表列出了检出的所有Westgard规则违例：
    </p>
    <ul>
      <li>每行列出了被触发的规则、涉及的数据点、质控水平以及严重程度（警告或拒绝）。</li>
      <li>警告类违例（1-2s）表示需要关注的点，但不需要拒绝批次。</li>
      <li>拒绝类违例（1-3s、2-2s、R-4s、4-1s、10x）表示未经调查不应报告该批次的结果。</li>
    </ul>
    <p>
      <strong>使用示例文件的预期结果：</strong>使用 <code>sample_qc_quantstudio.xlsx</code> 时，
      您将看到一组QC数据点以及计算出的汇总统计量。该数据旨在展示一个干净的数据集，所有点均在
      可接受限值以内。
    </p>
    <p>
      若要看到违例效果，可使用 <code>sample_qc_violations.xlsx</code>，其中包含触发各种
      Westgard规则的故意离群值。
    </p>

    <h3>步骤6：导出 QC 报告</h3>
    <p>
      点击页面顶部的导出按钮生成QC报告。报告包含：
    </p>
    <ul>
      <li>每个质控水平的汇总统计量（均值、SD、CV）。</li>
      <li>Levey-Jennings 图。</li>
      <li>所有 Westgard 违例清单。</li>
      <li>批次元数据（仪器、检测项目、批号）。</li>
      <li>时间戳和审计追踪引用。</li>
    </ul>

    <h2>Sigma 分析模块使用指南</h2>
    <p>
      Sigma 分析模块计算检测项目的 Sigma 指标，并推荐适当的QC策略。
    </p>

    <h3>步骤1：输入检测参数</h3>
    <p>
      从侧栏进入 <strong>Sigma 分析</strong>。为每个检测项目输入以下数值：
    </p>
    <ul>
      <li><strong>TEa（允许总误差）：</strong>分析项目的质量要求，以百分比表示。来源可参考CLIA、
        生物学变异数据库或制造商声明。</li>
      <li><strong>Bias（偏倚）：</strong>方法的系统误差，以百分比表示。从能力验证或方法比对研究中获取。</li>
      <li><strong>CV（变异系数）：</strong>方法的不精密度，以百分比表示。从您的QC数据中计算
        （至少20个数据点）。</li>
    </ul>

    <div class="info-box">
      <strong>可试用的示例值：</strong>TEa = 15%，Bias = 2.5%，CV = 3.0%。
      计算得出的 Sigma 约等于 4.2（良好性能）。
    </div>

    <h3>步骤2：点击计算</h3>
    <p>
      点击计算按钮。LabQC 应用 Sigma 公式：<code>sigma = (TEa - |Bias|) / CV</code>。
    </p>

    <h3>步骤3：阅读结果表</h3>
    <p>
      结果表显示：
    </p>
    <ul>
      <li>计算得出的 Sigma 值。</li>
      <li>性能分级（世界级、优秀、良好、临界、差、不可接受）。</li>
      <li>基于 Sigma 水平推荐的QC规则和质控品数量。</li>
    </ul>

    <h3>步骤4：解读 NMEDx 图</h3>
    <p>
      NMEDx（归一化方法决策）图绘制检测项目的性能：
    </p>
    <ul>
      <li>x轴表示归一化至TEa的不精密度（CV）。</li>
      <li>y轴表示归一化至TEa的偏倚。</li>
      <li>彩色带状区域显示 Sigma 分级区间（从世界级到不可接受）。</li>
      <li>您的检测项目在图上显示为一个点——其位置一目了然地告诉您存在多少安全裕度。</li>
    </ul>

    <h3>步骤5：遵循推荐的 QC 规则</h3>
    <p>
      基于计算得出的 Sigma 值，LabQC 推荐一套QC策略：
    </p>
    <ul>
      <li>应应用哪些 Westgard 规则。</li>
      <li>每批应运行多少个质控品（N=2 或 N=4）。</li>
      <li>当前方法性能是否充足或需要改进。</li>
    </ul>

    <h2>验证模块使用指南</h2>
    <p>
      验证模块引导您完成检测验证研究，提供统计分析和报告生成。
    </p>

    <h3>步骤1：选择验证类型</h3>
    <p>
      从侧栏进入 <strong>方法验证</strong>。选择验证研究类型：
    </p>
    <ul>
      <li><strong>LOD（检出限）：</strong>确定最低可检出浓度。</li>
      <li><strong>精密度：</strong>评估批内和批间变异性。</li>
      <li><strong>线性：</strong>验证可报告范围和扩增效率。</li>
    </ul>

    <h3>步骤2：上传数据集</h3>
    <p>
      上传包含验证数据的Excel文件：
    </p>
    <ul>
      <li><strong>LOD用：</strong>使用 <code>sample_validation_lod.xlsx</code>。文件应包含
        多个低浓度水平的重复测量值。</li>
      <li><strong>线性用：</strong>使用 <code>sample_validation_linearity.xlsx</code>。文件应包含
        跨系列稀释范围的测量值。</li>
    </ul>

    <h3>步骤3：定义接受标准</h3>
    <p>
      为研究设定接受标准：
    </p>
    <ul>
      <li>LOD：检出率阈值（通常95%）。</li>
      <li>精密度：最大可接受CV（批内通常5%，批间通常10%）。</li>
      <li>线性：最小R<sup>2</sup>（通常0.99）和可接受的斜率范围。</li>
    </ul>

    <h3>步骤4：运行验证</h3>
    <p>
      点击验证按钮。LabQC 根据所选研究类型执行相应的统计分析。
    </p>

    <h3>步骤5：解读结果</h3>
    <p>
      结果区域显示：
    </p>
    <ul>
      <li>计算出的统计量（LOD值、CV值、R<sup>2</sup>、斜率等）。</li>
      <li>对照接受标准的合格/不合格判定。</li>
      <li>可视化图表（线性散点图、精密度分布图）。</li>
      <li>可下载的验证报告。</li>
    </ul>

    <h2>批号注册模块使用指南</h2>
    <p>
      批号注册功能追踪试剂和质控品批号，实现可追溯性和批间对比。
    </p>
    <ol>
      <li>从侧栏进入 <strong>批号管理</strong>。</li>
      <li>点击添加新批号条目。</li>
      <li>输入批号详情：批号编号、物料类型（试剂或质控品）、制造商、有效期及备注。</li>
      <li>保存条目，它将出现在注册表中。</li>
      <li>上传QC数据时引用批号ID，将各批次与特定批号关联。</li>
      <li>利用注册表追踪批号变更时机，并将批号转换与QC性能变化进行关联分析。</li>
    </ol>

    <h2>审计追踪模块使用指南</h2>
    <p>
      审计追踪提供所有系统活动的防篡改记录。
    </p>
    <ol>
      <li>从侧栏进入 <strong>审计追踪</strong>。</li>
      <li>主视图显示所有操作的时间顺序列表（上传、分析、导出、配置变更）。</li>
      <li>每个条目显示时间戳、用户、操作类型和详情。</li>
      <li>使用筛选选项按日期范围、操作类型或用户筛选。</li>
      <li>点击 <strong>验证完整性</strong> 运行哈希链验证。系统将确认整个审计追踪是否完好无损，
        或识别出任何断裂环节。</li>
      <li>使用导出功能生成审计追踪报告供法规审查。</li>
    </ol>

    <div class="warning-box">
      <strong>注意：</strong>审计追踪仅为追加模式。条目不能通过应用界面编辑或删除。
      这是有意设计的——法规要求审计记录为不可篡改的。
    </div>

    <h2>法规助手使用指南</h2>
    <p>
      法规助手利用AI帮助回答与临床实验室QC相关的法规和合规性问题。
    </p>

    <h3>前提条件</h3>
    <ul>
      <li>使用法规助手前必须在<strong>系统设置</strong>中配置API密钥。</li>
      <li>进入系统设置，找到API密钥配置区域并输入您的密钥。</li>
    </ul>

    <h3>使用助手</h3>
    <ol>
      <li>从侧栏进入 <strong>法规查询</strong>。</li>
      <li>在输入区域键入您的问题。示例：
        <ul>
          <li>"ISO 15189:2022 对QC有哪些要求？"</li>
          <li>"根据CLIA应多久运行一次QC？"</li>
          <li>"CDSCO IVD注册需要哪些文件？"</li>
        </ul>
      </li>
      <li>助手提供基于法规标准和实验室最佳实践的答复。</li>
      <li>将答复作为合规文档编写的起点——务必与法规原文进行核对。</li>
    </ol>

    <div class="info-box">
      <strong>免责声明：</strong>法规助手是参考工具，不能替代专业的法规咨询。
      所有关键合规决策请务必与您的质量负责人和法规事务团队核实。
    </div>
  </div>
</template>
