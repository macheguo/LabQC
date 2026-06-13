<script setup>
import PlotlyNMEDxDiagram from './PlotlyNMEDxDiagram.vue'
</script>

<template>
  <div class="learn-content">
    <h1>第三章：实验室中的六西格玛</h1>
    <p class="chapter-subtitle">运用 Sigma 指标客观衡量检测质量，设计最优的 QC 策略。</p>

    <h2>六西格玛对实验室质量的意义</h2>
    <p>
      六西格玛最初是摩托罗拉在20世纪80年代提出、由通用电气推广的质量管理方法论。在制造业中，
      六西格玛的目标是每百万次机会中缺陷不超过3.4个。当应用于临床实验室时，它提供了一个衡量
      分析方法相对于其质量需求表现如何的通用指标。
    </p>
    <p>
      核心理念很简单：将<strong>允许总误差</strong>（可接受多少误差）与<strong>实际误差</strong>
      （方法实际产生多少误差）进行比较。该比值以 Sigma 指标表达，告诉你在方法的实际表现与产生
      临床不可接受结果之间，还有多少个标准差的"安全裕度"。
    </p>
    <p>
      Sigma值越高，意味着方法越可靠、安全裕度越大；Sigma值越低，意味着方法正在接近其质量限值运行，
      需要更严格的QC来在误差影响患者结果前捕获它们。
    </p>

    <h2>Sigma 指标计算公式</h2>
    <p>
      实验室方法的 Sigma 指标按下式计算：
    </p>
    <pre class="diagram">
             TEa - |Bias|
      sigma = -----------
                 CV

  其中:
    TEa   = 允许总误差 (%)
    Bias  = 系统误差 / 不准确度 (%)
    CV    = 变异系数 / 不精密度 (%)
    </pre>

    <h3>理解每个组成部分</h3>
    <ul>
      <li>
        <strong>TEa（允许总误差）：</strong>对于某个分析项目，在不影响临床决策的前提下可接受的最大误差量。
        TEa值由法规机构、生物学变异数据库和专家共识制定。例如，若某新冠病毒Ct值的TEa为15%，
        则方法必须产生在真值15%以内的结果。
      </li>
      <li>
        <strong>Bias（偏倚）：</strong>系统误差分量——方法平均值与真值（参考值）之间的持续差异。
        偏倚通常通过能力验证（外部质量评估）、方法比对研究或回收实验来估算，以百分比表示。
      </li>
      <li>
        <strong>CV（变异系数）：</strong>随机误差分量——方法的不精密度，以占均值的百分比表示。
        CV 由QC数据计算：<code>(SD / 均值) × 100</code>。它代表方法在批次间的变异性。
      </li>
    </ul>

    <h2>Sigma 分级表</h2>
    <p>
      Sigma值被分类为不同的性能等级，直接指导QC设计决策：
    </p>

    <table>
      <thead>
        <tr>
          <th>Sigma</th>
          <th>分级</th>
          <th>缺陷率</th>
          <th>QC 建议</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>&ge; 6</strong></td>
          <td style="color: #43A047;">世界级 (World Class)</td>
          <td>每百万3.4</td>
          <td>只需少量QC。1-3s规则搭配N=2个质控品即可。</td>
        </tr>
        <tr>
          <td><strong>5 - 6</strong></td>
          <td style="color: #66BB6A;">优秀 (Excellent)</td>
          <td>每百万233</td>
          <td>标准QC。Westgard多规则搭配N=2个质控品。</td>
        </tr>
        <tr>
          <td><strong>4 - 5</strong></td>
          <td style="color: #F9A825;">良好 (Good)</td>
          <td>每百万6,210</td>
          <td>需要加强QC。建议多规则搭配N=4个质控品。</td>
        </tr>
        <tr>
          <td><strong>3 - 4</strong></td>
          <td style="color: #FF9800;">临界 (Marginal)</td>
          <td>每百万66,807</td>
          <td>需要最大力度QC。N=4多规则并收紧限值。考虑改进方法。</td>
        </tr>
        <tr>
          <td><strong>2 - 3</strong></td>
          <td style="color: #E53935;">差 (Poor)</td>
          <td>每百万308,538</td>
          <td>未显著改进前不可常规使用。可能需要更换方法。</td>
        </tr>
        <tr>
          <td><strong>&lt; 2</strong></td>
          <td style="color: #B71C1C;">不可接受 (Unacceptable)</td>
          <td>&gt;每百万308,538</td>
          <td>方法不能满足质量要求。更换或从根本上重新设计。</td>
        </tr>
      </tbody>
    </table>

    <h2>NMEDx（归一化方法决策）图</h2>
    <p>
      NMEDx图是一种可视化工具，将方法的性能绘制在二维空间中：x轴为不精密度（CV占TEa的比例），
      y轴为偏倚（占TEa的比例）。这一归一化处理使不同TEa值的方法能在同一张图上进行比较。
    </p>
    <PlotlyNMEDxDiagram
      :assays="[
        { name: '新冠病毒', cvTEa: 0.08, biasTEa: 0.15, sigma: 5.8 },
        { name: '甲型流感', cvTEa: 0.12, biasTEa: 0.30, sigma: 4.2 },
        { name: '呼吸道合胞病毒', cvTEa: 0.18, biasTEa: 0.45, sigma: 2.8 },
        { name: 'HBV 病毒载量', cvTEa: 0.05, biasTEa: 0.10, sigma: 6.5 },
        { name: 'HCV 基因分型', cvTEa: 0.15, biasTEa: 0.35, sigma: 3.5 },
      ]"
    />

    <p>
      LabQC 中的 NMEDx 图根据每个方法的 Sigma 等级进行颜色编码，让哪些项目运行良好、
      哪些需要关注一目了然。
    </p>

    <h2>Sigma 值如何驱动 QC 设计</h2>
    <p>
      Sigma指标的实用价值在于，它直接决定了需要哪些QC规则以及需要多少个质控品。高Sigma方法
      需要的QC较少，因为足以影响患者的误差极其罕见。低Sigma方法则需要严格的QC，
      因为方法正在接近其质量限值运行。
    </p>

    <table>
      <thead>
        <tr>
          <th>Sigma</th>
          <th>推荐 QC 规则</th>
          <th>每批次质控品数</th>
          <th>频次</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>&ge; 6</strong></td>
          <td>仅 1-3s</td>
          <td>N = 2</td>
          <td>标准（每批次或每日）</td>
        </tr>
        <tr>
          <td><strong>5 - 6</strong></td>
          <td>1-3s / 2-2s / R-4s</td>
          <td>N = 2</td>
          <td>标准</td>
        </tr>
        <tr>
          <td><strong>4 - 5</strong></td>
          <td>1-3s / 2-2s / R-4s / 4-1s</td>
          <td>N = 4</td>
          <td>每批次</td>
        </tr>
        <tr>
          <td><strong>3 - 4</strong></td>
          <td>全部 Westgard 多规则</td>
          <td>N = 4</td>
          <td>每批次，加重复检测</td>
        </tr>
        <tr>
          <td><strong>&lt; 3</strong></td>
          <td>单独QC不足够</td>
          <td>不适用</td>
          <td>需先改进方法再设计QC</td>
        </tr>
      </tbody>
    </table>

    <div class="info-box">
      <strong>实用提示：</strong>LabQC 在计算出检测项目的 Sigma 指标后，自动根据上表
      推荐相应的QC规则和质控策略。请用 Sigma 分析模块评估实验室中的每项检测。
    </div>

    <h2>TEa 的来源</h2>
    <p>
      选择合适的TEa至关重要——它定义了计算 Sigma 指标所依据的质量目标。常见来源包括：
    </p>
    <ul>
      <li>
        <strong>CLIA（临床实验室改进修正案）：</strong>美国联邦计划为受监管的分析项目
        公布固定的允许误差限值。这些被广泛用作基线，不过可能比基于生物学导出的目标更为宽泛。
      </li>
      <li>
        <strong>生物学变异数据库：</strong>TEa可由个体内和个体间生物学变异导出，公式为
        <code>TEa = 1.65 × CV_i + 0.25 × (CV_i² + CV_g²)^0.5</code>，其中 CV_i 为个体内变异、
        CV_g 为个体间变异。欧洲临床化学联合会(EFLM)维护着全面的生物学变异数据库。
      </li>
      <li>
        <strong>CDSCO（印度中央药物标准控制组织）：</strong>印度的法规机构参考ISO 15189和
        制造商声明的性能要求。对于在印度上市的IVD设备，制造商声明的性能规格作为TEa基准。
      </li>
      <li>
        <strong>临床决策限值：</strong>对于某些分析项目，TEa由临床决策点导出——即诊断决策发生
        改变的浓度。允许误差必须足够小，使接近决策点的结果能够被可靠分类。
      </li>
      <li>
        <strong>专家共识（如 RCPA、RiliBaK）：</strong>各国专业组织发布共识质量目标。
        澳大利亚皇家病理学家学会(RCPA)和德国医学会(RiliBaK)指南被广泛引用。
      </li>
    </ul>

    <div class="warning-box">
      <strong>重要提示：</strong>始终记录TEa值的来源。在法规审查中，你需要为每个分析项目
      所选择的TEa提供理由。使用公认的已出版来源（CLIA、生物学变异或制造商声明）可提供最强的
      可辩护依据。
    </div>
  </div>
</template>
