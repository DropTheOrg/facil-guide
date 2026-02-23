/**
 * Extract steps from guide markdown body for HowTo schema.
 * Matches patterns like:
 *   ### Step 1: Title (EN)
 *   ### Etape 1 : Title (FR)
 *   ### Paso 1: Title (ES)
 *   ### Passo 1: Title (PT)
 *   ### Passaggio 1: Title (IT)
 */
export function extractSteps(body: string): { title: string; text: string }[] {
  const steps: { title: string; text: string }[] = [];

  // Split by ### headings that look like steps
  const stepPattern = /^#{2,3} (?:Step|Etape|Paso|Passo|Passaggio)\s*\d+\s*[:\uff1a]\s*(.+)$/gm;
  const matches = [...body.matchAll(stepPattern)];

  for (let i = 0; i < matches.length; i++) {
    const title = matches[i][1].trim();
    const startIdx = matches[i].index! + matches[i][0].length;
    const endIdx = i + 1 < matches.length ? matches[i + 1].index! : body.length;
    const textBlock = body.slice(startIdx, endIdx).trim();

    // Get first paragraph as step text (strip markdown bold/links)
    const firstPara = textBlock.split('\n\n')[0]
      .replace(/\*\*([^*]+)\*\*/g, '$1')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\n/g, ' ')
      .trim();

    if (title && firstPara) {
      steps.push({ title, text: firstPara });
    }
  }

  return steps;
}
