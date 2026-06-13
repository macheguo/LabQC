<script setup>
</script>

<template>
  <div class="learn-content">
    <h1>第七章：示例数据集参考</h1>
    <p class="chapter-subtitle">LabQC 附带的示例文件完整指南，以及每个文件的预期结果。</p>

    <h2>概述</h2>
    <p>
      LabQC 在 <code>backend/data/samples/</code> 目录中附赠了一套示例数据集。这些文件旨在
      帮助您测试软件的每个模块并验证其功能是否正常。每个文件都经过精心设计，以演示特定功能并产生
      可预测、可验证的结果。
    </p>
    <p>
      在首次安装LabQC、系统升级或培训新实验室人员时，可使用这些文件进行测试。
    </p>

    <h2>示例文件清单</h2>

    <table>
      <thead>
        <tr>
          <th>文件名</th>
          <th>模块</th>
          <th>说明</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>sample_qc_quantstudio.xlsx</code></td>
          <td>QC 监测</td>
          <td>QuantStudio导出格式的标准QC数据集，含多个质控水平的Ct值。</td>
        </tr>
        <tr>
          <td><code>sample_qc_violations.xlsx</code></td>
          <td>QC 监测</td>
          <td>含故意离群值的QC数据集，用于触发Westgard规则违例。</td>
        </tr>
        <tr>
          <td><code>sample_sigma_inputs.xlsx</code></td>
          <td>Sigma 分析</td>
          <td>多个检测项目预计算的TEa、Bias和CV值，用于Sigma指标计算。</td>
        </tr>
        <tr>
          <td><code>sample_validation_lod.xlsx</code></td>
          <td>方法验证（LOD）</td>
          <td>检出限附近系列稀释浓度的重复测量数据。</td>
        </tr>
        <tr>
          <td><code>sample_validation_linearity.xlsx</code></td>
          <td>方法验证（线性）</td>
          <td>覆盖宽浓度范围的系列稀释数据，用于评估线性。</td>
        </tr>
      </tbody>
    </table>

    <h2>各文件详细说明与预期结果</h2>

    <h3>sample_qc_quantstudio.xlsx</h3>
    <p>
      <strong>适用模块：</strong>QC 监测<br>
      <strong>格式：</strong>模拟QuantStudio导出的文件，含样本标识和Ct值<br>
      <strong>内容：</strong>各质控水平的QC数据，Ct值围绕已确认的均值分布
    </p>
    <p><strong>使用方法：</strong></p>
    <ol>
      <li>进入 QC 监测。</li>
      <li>上传文件，可选填元数据（仪器："QuantStudio 5"，检测项目："SARS-CoV-2"）。</li>
      <li>点击上传并分析。</li>
    </ol>
    <p><strong>预期结果：</strong></p>
    <ul>
      <li>应为质控数据计算出汇总统计量。</li>
      <li>Levey-Jennings 图应显示围绕均值分布的数据点，大多数点在±2SD以内。</li>
      <li>这是一个干净的数据集——不应看到任何拒绝级违例，但接近±2SD的个别点可能触发1-2s警告。</li>
      <li>整体批次状态应为通过。</li>
    </ul>

    <div class="info-box">
      <strong>验证检查：</strong>上传后，确认Levey-Jennings图能正确渲染且SD线标签清晰，
      以及汇总统计表中均值、SD和CV显示合理的数值。
    </div>

    <h3>sample_qc_violations.xlsx</h3>
    <p>
      <strong>适用模块：</strong>QC 监测<br>
      <strong>格式：</strong>与QuantStudio文件结构相同<br>
      <strong>内容：</strong>包含故意放置的离群值的QC数据，用于触发Westgard规则违例
    </p>
    <p><strong>使用方法：</strong></p>
    <ol>
      <li>进入 QC 监测。</li>
      <li>上传文件。</li>
      <li>点击上传并分析。</li>
    </ol>
    <p><strong>预期结果：</strong></p>
    <ul>
      <li>Levey-Jennings 图应显示一个或多个数据点明显在±2SD或±3SD线之外。</li>
      <li>违例表应列出具体的Westgard规则违例，并标识受影响的各个数据点。</li>
      <li>预期可看到1-3s（点超出±3SD）以及可能的2-2s（连续点在同一侧超出±2SD）违例。</li>
      <li>由于存在拒绝级违例，整体批次状态应为失败。</li>
    </ul>

    <div class="warning-box">
      <strong>培训练习：</strong>用此文件练习纠正措施工作流程。当检测到违例时，记录在真实实验室
      情境下您将采取的调查步骤：核查数据点、识别被触发规则、确定潜在根本原因、描述纠正措施。
    </div>

    <h3>sample_sigma_inputs.xlsx</h3>
    <p>
      <strong>适用模块：</strong>Sigma 分析<br>
      <strong>格式：</strong>表格数据，包含检测名称、TEa、Bias和CV列<br>
      <strong>内容：</strong>多个假设检测项目的预计算质量参数
    </p>
    <p><strong>使用方法：</strong></p>
    <ol>
      <li>进入 Sigma 分析。</li>
      <li>您可以从该文件中手动输入数值，或将其作为预期输入格式的参考。</li>
      <li>输入某个检测项目的TEa、Bias和CV值。</li>
      <li>点击计算。</li>
    </ol>
    <p><strong>预期结果：</strong></p>
    <ul>
      <li>Sigma 指标应使用公式 <code>sigma = (TEa - |Bias|) / CV</code> 正确计算。</li>
      <li>分级应与Sigma等级区间匹配（如 Sigma &ge; 6 = 世界级，5-6 = 优秀等）。</li>
      <li>NMEDx图应将检测项目绘入正确的分级区域。</li>
      <li>QC 建议应适合计算出的Sigma水平。</li>
    </ul>

    <h3>sample_validation_lod.xlsx</h3>
    <p>
      <strong>适用模块：</strong>方法验证（LOD研究）<br>
      <strong>格式：</strong>多个低浓度水平的重复Ct值<br>
      <strong>内容：</strong>预期检出限附近的系列稀释浓度测量数据
    </p>
    <p><strong>使用方法：</strong></p>
    <ol>
      <li>进入方法验证。</li>
      <li>选择 LOD 作为验证类型。</li>
      <li>上传文件。</li>
      <li>设定检出率阈值（默认使用95%）。</li>
      <li>运行验证。</li>
    </ol>
    <p><strong>预期结果：</strong></p>
    <ul>
      <li>LOD 应根据检出率达到或超过阈值的最低浓度计算得出。</li>
      <li>较高浓度水平应显示100%检出率。</li>
      <li>较低浓度水平应显示逐渐下降的检出率。</li>
      <li>结果应包含确定的LOD值的明确声明。</li>
    </ul>

    <h3>sample_validation_linearity.xlsx</h3>
    <p>
      <strong>适用模块：</strong>方法验证（线性研究）<br>
      <strong>格式：</strong>跨系列稀释梯度测量的Ct值<br>
      <strong>内容：</strong>覆盖宽浓度范围用于评估线性的数据
    </p>
    <p><strong>使用方法：</strong></p>
    <ol>
      <li>进入方法验证。</li>
      <li>选择线性作为验证类型。</li>
      <li>上传文件。</li>
      <li>设定接受标准（R<sup>2</sup> &ge; 0.99，斜率 -3.1 至 -3.6）。</li>
      <li>运行验证。</li>
    </ol>
    <p><strong>预期结果：</strong></p>
    <ul>
      <li>回归分析应产出接近或超过0.99的R<sup>2</sup>值。</li>
      <li>斜率应在PCR效率的可接受范围内。</li>
      <li>散点图应显示数据点紧密跟随回归线。</li>
      <li>若接受标准达成，验证结果应为通过。</li>
    </ul>

    <h2>快速参考表</h2>
    <p>
      测试 LabQC 各模块时可使用此表快速查阅：
    </p>

    <table>
      <thead>
        <tr>
          <th>文件</th>
          <th>模块</th>
          <th>预期结果</th>
          <th>关键验证点</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>sample_qc_quantstudio.xlsx</code></td>
          <td>QC 监测</td>
          <td>通过 — 所有点在限值内</td>
          <td>L-J 图正确渲染，统计量已计算</td>
        </tr>
        <tr>
          <td><code>sample_qc_violations.xlsx</code></td>
          <td>QC 监测</td>
          <td>失败 — 检出Westgard违例</td>
          <td>违例表已填充，图表高亮离群值</td>
        </tr>
        <tr>
          <td><code>sample_sigma_inputs.xlsx</code></td>
          <td>Sigma 分析</td>
          <td>各检测项目 Sigma 指标已计算</td>
          <td>NMEDx图已绘制，QC建议已显示</td>
        </tr>
        <tr>
          <td><code>sample_validation_lod.xlsx</code></td>
          <td>方法验证</td>
          <td>LOD 在正确浓度确定</td>
          <td>各浓度水平的检出率已计算</td>
        </tr>
        <tr>
          <td><code>sample_validation_linearity.xlsx</code></td>
          <td>方法验证</td>
          <td>通过 — R<sup>2</sup> &ge; 0.99</td>
          <td>回归线已绘制，斜率和R<sup>2</sup>已显示</td>
        </tr>
      </tbody>
    </table>

    <div class="info-box">
      <strong>提示：</strong>请将这些示例文件保持可访问状态，以便新员工入职培训时使用。
      与新团队成员逐一展示每个文件的测试流程，是培训他们理解软件操作和基础QC概念的有效方式。
    </div>
  </div>
</template>
