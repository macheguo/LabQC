/**
 * Print the current page as a PDF report.
 * Temporarily injects a print header with report metadata,
 * triggers window.print(), then cleans up.
 */
export function printReport({ title, subtitle, generatedAt } = {}) {
  const header = document.createElement('div')
  header.className = 'print-report-header'
  header.innerHTML = `
    <div class="print-report-header__logo">LabQC - 凯思康</div>
    <h1 class="print-report-header__title">${title || document.title}</h1>
    ${subtitle ? `<p class="print-report-header__subtitle">${subtitle}</p>` : ''}
    <p class="print-report-header__meta">生成时间：${generatedAt || new Date().toLocaleString()} | 凯思康 LabQC 质控平台</p>
    <hr class="print-report-header__divider" />
  `
  document.body.prepend(header)

  window.print()

  // Clean up after print dialog closes
  setTimeout(() => header.remove(), 500)
}
