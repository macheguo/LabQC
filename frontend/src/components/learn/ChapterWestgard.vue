<script setup>
import PlotlyLJDiagram from './PlotlyLJDiagram.vue'
</script>

<template>
  <div class="learn-content">
    <h1>第二章：Westgard 规则详解</h1>
    <p class="chapter-subtitle">判断QC批次应接受还是拒绝的统计学规则。</p>

    <h2>历史：James Westgard 是谁？</h2>
    <p>
      James O. Westgard 博士是美国临床化学家，于1981年与合作者共同发表了多规则QC的开创性论文。
      在Westgard的工作之前，实验室依赖简单的控制限（通常是均值±2SD或±3SD）来决定接受或拒绝分析批次。
      这些单规则方法有明显的局限性：2SD规则拒绝了太多实际可接受的批次（假拒绝率高），而3SD规则
      漏掉了大量确实存在误差的批次（误差检出能力差）。
    </p>
    <p>
      Westgard的洞见在于将多个规则组合为顺序评估。通过使用不同规则检测不同类型的误差——随机误差、
      系统误差和趋势——多规则方法同时实现了低假拒绝率和高误差检出率。这套"Westgard多规则"
      系统已成为临床实验室QC的全球标准。
    </p>

    <h2>Levey-Jennings 图</h2>
    <p>
      Levey-Jennings（L-J）图是QC监测的主要可视化工具。它将质控值按时间顺序绘制，与基于该质控品
      已有均值和标准差（SD）得出的统计限值进行对比。
    </p>

    <PlotlyLJDiagram
      title="Levey-Jennings 图 — 正常QC批次"
      :points="[
        {x:1, y:25.2, color:'normal'}, {x:2, y:24.8, color:'normal'},
        {x:3, y:25.5, color:'normal'}, {x:4, y:24.6, color:'normal'},
        {x:5, y:25.1, color:'normal'}, {x:6, y:25.3, color:'normal'},
        {x:7, y:24.9, color:'normal'},
      ]"
      :mean="25" :sd="0.5"
    />

    <h3>如何阅读 L-J 图</h3>
    <ul>
      <li><strong>中心线</strong>代表该质控品经确认的均值Ct值，由验证期间至少20个数据点计算得出。</li>
      <li><strong>SD线</strong>（±1SD、±2SD、±3SD）将图划分为多个区域。约68%的值应落在±1SD内，
        95%在±2SD内，99.7%在±3SD内。</li>
      <li><strong>时间趋势</strong>与单个数据点同样重要。即使没有任何单点超出2SD，逐渐向均值一侧漂移
        也可能提示正在发展的系统误差。</li>
    </ul>

    <h2>QC上下文中的均值、SD和z分数</h2>
    <p>
      在应用Westgard规则之前，实验室必须为每个质控水平建立统计参数：
    </p>
    <ul>
      <li><strong>均值（Mean）：</strong>来自验证数据集的平均Ct值（至少20次运行，理想情况下跨20个不同工作日，以捕获日间变异）。</li>
      <li><strong>标准差（SD）：</strong>Ct值围绕均值的离散度。SD越小表示精密度越高。</li>
      <li><strong>z分数：</strong>一个数据点与均值相差的标准差数。计算方式：<code>z = (观测值 - 均值) / SD</code>。z分数为+2.0表示该值正好在均值之上2SD。</li>
    </ul>
    <p>
      Westgard规则本质上基于z分数，尽管为便于理解常以SD单位表述。
    </p>

    <h2>六条 Westgard 规则</h2>
    <p>
      LabQC 按以下顺序评估六条规则。第一条规则（<strong>1-2s</strong>）为警告，触发后即评估其余拒绝规则。
    </p>

    <h3>1-2s 规则（警告）</h3>
    <p>
      <strong>定义：</strong>单个质控观测值超出均值±2SD。
    </p>
    <p>
      <strong>解读：</strong>这<em>仅是警告规则</em>——本身并不导致拒绝。当检测到1-2s违例时，必须评估
      剩余拒绝规则。在正态分布的数据集中，约有1/20（5%）的QC值会仅凭偶然超出±2SD，因此该规则用作筛选触发器。
    </p>
    <PlotlyLJDiagram
      title="1-2s 规则 — 警告"
      :points="[
        {x:1, y:25.1, color:'normal'}, {x:2, y:24.8, color:'normal'},
        {x:3, y:26.2, color:'warning'}, {x:4, y:25.0, color:'normal'},
        {x:5, y:24.7, color:'normal'}, {x:6, y:25.3, color:'normal'},
      ]"
      :mean="25" :sd="0.5"
      annotation="第3点超出 +2SD — 警告触发"
    />

    <h3>1-3s 规则（拒绝）</h3>
    <p>
      <strong>定义：</strong>单个质控观测值超出均值±3SD。
    </p>
    <p>
      <strong>解读：</strong>这表明存在较大的随机误差或重大系统误差的开始。统计学上仅约0.3%的值应落在
      ±3SD之外。一旦出现，必须拒绝该批次。常见原因包括样本混淆、移液错误、试剂失效或仪器故障。
    </p>
    <PlotlyLJDiagram
      title="1-3s 规则 — 拒绝"
      :points="[
        {x:1, y:25.0, color:'normal'}, {x:2, y:26.8, color:'reject'},
        {x:3, y:25.2, color:'normal'}, {x:4, y:24.9, color:'normal'},
      ]"
      :mean="25" :sd="0.5"
      annotation="第2点超出 +3SD — 批次被拒绝"
    />

    <h3>2-2s 规则（拒绝）</h3>
    <p>
      <strong>定义：</strong>连续两个质控观测值超出均值+2SD，或两个均低于均值-2SD
      （即连续两个点处于±2SD之外的<em>同一侧</em>）。
    </p>
    <p>
      <strong>解读：</strong>该规则用于检测系统误差——某一方向的持续偏移或偏倚。可适用于单批次内
      （若测量多个质控品）或跨连续批次的场景。常见原因包括校准漂移、试剂批号老化或环境条件变化。
    </p>
    <PlotlyLJDiagram
      title="2-2s 规则 — 拒绝"
      :points="[
        {x:1, y:25.1, color:'normal'}, {x:2, y:26.15, color:'reject'},
        {x:3, y:26.20, color:'reject'}, {x:4, y:25.0, color:'normal'},
      ]"
      :mean="25" :sd="0.5"
      annotation="第2-3点均超出 +2SD — 检出系统误差"
    />

    <h3>R-4s 规则（拒绝）</h3>
    <p>
      <strong>定义：</strong>单批次内两个质控观测值之间的极差超过4SD（一个超出+2SD而另一个低于-2SD，或反之）。
    </p>
    <p>
      <strong>解读：</strong>该规则检测单分析批次内的大随机误差。仅当同一批次内测量了两个不同水平的质控品
      （如L1和L2）时适用。若一个偏高而另一个偏低，总极差（range）就表明精密度差。常见原因
      包括某一质控品的移液错误、光路气泡或孔间变异性。
    </p>
    <PlotlyLJDiagram
      title="R-4s 规则 — 拒绝（批内）"
      :points="[
        {x:1, y:26.2, color:'reject'}, {x:1, y:23.5, color:'reject'},
      ]"
      :mean="25" :sd="0.5"
      annotation="同批次内 L1在+2.4SD，L2在-3.0SD — 极差 > 4SD"
    />

    <h3>4-1s 规则（拒绝）</h3>
    <p>
      <strong>定义：</strong>连续四个质控观测值均超出均值+1SD，或均低于均值-1SD
      （即连续四个点处于±1SD之外的<em>同一侧</em>）。
    </p>
    <p>
      <strong>解读：</strong>该规则检测微小但持续的系统误差。每个单独点可能看似正常，但四个连续点
      全部向同一方向偏移的模式在统计学上不太可能发生（正常条件下概率约6%），表明存在真实偏倚。
      常见原因包括试剂逐渐老化、仪器轻微漂移，或新批号质控品的目标值与旧批次略有不同。
    </p>
    <PlotlyLJDiagram
      title="4-1s 规则 — 拒绝"
      :points="[
        {x:1, y:25.0, color:'normal'}, {x:2, y:25.7, color:'reject'},
        {x:3, y:25.8, color:'reject'}, {x:4, y:25.6, color:'reject'},
        {x:5, y:25.65, color:'reject'}, {x:6, y:25.1, color:'normal'},
      ]"
      :mean="25" :sd="0.5"
      annotation="第2-5点均在 +1SD 之上 — 系统偏移"
    />

    <h3>10x 规则（拒绝）</h3>
    <p>
      <strong>定义：</strong>连续十个质控观测值落在均值的同一侧（无论距均值多远）。
    </p>
    <p>
      <strong>解读：</strong>该规则检测极微小但持续的系统误差或偏倚。每个单独点都可能完全在可接受限值内，
      但连续十个点全部落在均值同一侧的概率仅约0.1%（2<sup>-10</sup>）。该模式是分析系统发生真实偏移的
      强有力指标。常见原因包括试剂浓度在数周内缓慢变化、环境漂移，或仪器校准的细微变化。
    </p>
    <PlotlyLJDiagram
      title="10x 规则 — 拒绝"
      :points="[
        {x:1, y:25.1, color:'reject'}, {x:2, y:25.3, color:'reject'},
        {x:3, y:25.05, color:'reject'}, {x:4, y:25.2, color:'reject'},
        {x:5, y:25.15, color:'reject'}, {x:6, y:25.4, color:'reject'},
        {x:7, y:25.25, color:'reject'}, {x:8, y:25.1, color:'reject'},
        {x:9, y:25.35, color:'reject'}, {x:10, y:25.2, color:'reject'},
        {x:11, y:24.9, color:'normal'}, {x:12, y:25.0, color:'normal'},
      ]"
      :mean="25" :sd="0.5"
      annotation="第1-10点均高于均值 — 持续性偏倚"
    />

    <h2>Westgard 规则汇总表</h2>

    <table>
      <thead>
        <tr>
          <th>规则</th>
          <th>类型</th>
          <th>条件</th>
          <th>检出的误差</th>
          <th>处理措施</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1-2s</strong></td>
          <td>警告</td>
          <td>1个点超出±2SD</td>
          <td>筛选触发器</td>
          <td>评估其他规则</td>
        </tr>
        <tr>
          <td><strong>1-3s</strong></td>
          <td>拒绝</td>
          <td>1个点超出±3SD</td>
          <td>大随机误差</td>
          <td>拒绝批次</td>
        </tr>
        <tr>
          <td><strong>2-2s</strong></td>
          <td>拒绝</td>
          <td>连续2个点超出±2SD，同一侧</td>
          <td>系统误差</td>
          <td>拒绝批次</td>
        </tr>
        <tr>
          <td><strong>R-4s</strong></td>
          <td>拒绝</td>
          <td>批内极差超过4SD</td>
          <td>大随机误差</td>
          <td>拒绝批次</td>
        </tr>
        <tr>
          <td><strong>4-1s</strong></td>
          <td>拒绝</td>
          <td>连续4个点超出±1SD，同一侧</td>
          <td>系统误差</td>
          <td>拒绝批次</td>
        </tr>
        <tr>
          <td><strong>10x</strong></td>
          <td>拒绝</td>
          <td>连续10个点在均值同一侧</td>
          <td>微小持续偏倚</td>
          <td>拒绝批次</td>
        </tr>
      </tbody>
    </table>

    <h2>规则评估顺序与多规则方法</h2>
    <p>
      Westgard多规则系统按特定顺序评估：
    </p>
    <ol>
      <li>用 <strong>1-2s</strong> 规则检查当前数据点。若点在±2SD以内，则批次通过——无需进一步评估。</li>
      <li>若1-2s触发（警告），检查 <strong>1-3s</strong>。若点超出±3SD，立即拒绝。</li>
      <li>若1-3s未触发，用当前点和前一个数据点检查 <strong>2-2s</strong>。</li>
      <li>若同一批次内测量了多个质控水平，检查 <strong>R-4s</strong>。</li>
      <li>用当前点及前三个数据点检查 <strong>4-1s</strong>。</li>
      <li>用当前点及前九个数据点检查 <strong>10x</strong>。</li>
    </ol>
    <p>
      这种顺序方法在最大限度地减少假拒绝的同时，保持了检出真实分析误差的高灵敏度。
      LabQC 在分析上传的QC数据时，自动执行上述精确评估顺序。
    </p>

    <h2>拒绝批次 vs. 展开调查</h2>
    <p>
      并非所有规则违例都需要相同的响应：
    </p>
    <ul>
      <li><strong>仅1-2s警告：</strong>不拒绝。记录并监测。若下一批次正常，该单次离群值可能是随机变异。</li>
      <li><strong>1-3s违例：</strong>拒绝批次。用新质控品重新检测。若重测通过，原始失败很可能为随机事件
        （移液错误、气泡等）。若重测也失败，深入调查（试剂批号、仪器校准）。</li>
      <li><strong>2-2s或4-1s违例：</strong>提示系统误差。检查近期变化：新试剂批号？新质控品批号？
        仪器维护？操作人员变更？环境变化（温湿度）？</li>
      <li><strong>R-4s违例：</strong>检查批内问题：移液技术、样本完整性、反应孔位置效应。</li>
      <li><strong>10x违例：</strong>回顾过去若干批次的变化趋势。这通常预示着需要重新校准或建立新基线的
        渐进性偏移。</li>
    </ul>

    <div class="warning-box">
      <strong>重要提示：</strong>切勿压制或忽视任何Westgard违例。每条违例都必须记录、调查和解决。
      法规审查员会核查您的QC记录，期望看到每次失控事件的纠正措施证据。
    </div>
  </div>
</template>
