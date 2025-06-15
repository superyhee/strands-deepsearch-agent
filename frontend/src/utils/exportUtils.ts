/**
 * Export utilities for reports
 */

/**
 * Export content as Markdown file
 */
export const exportAsMarkdown = (content: string, filename: string = 'report.md') => {
  try {
    // Create blob with markdown content
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Error exporting markdown:', error);
    return false;
  }
};

/**
 * Open content in a new blank window for viewing/printing
 */
export const exportAsPDF = async (
  elementId: string,
  filename: string = 'report.pdf',
  title: string = 'Research Report'
): Promise<boolean> => {
  try {
    const element = document.getElementById(elementId);
    if (!element) {
      console.error('Element not found for PDF export');
      return false;
    }

    // Create a new window for viewing
    const newWindow = window.open('', '_blank');
    if (!newWindow) {
      console.error('Failed to open new window');
      return false;
    }

    // Clone the element content
    const clonedElement = element.cloneNode(true) as HTMLElement;

    // Extract the first heading as title
    const extractTitle = (element: HTMLElement): string => {
      // Try to find the first heading (h1, h2, h3, h4, h5, h6)
      const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6');
      if (headings.length > 0) {
        const firstHeading = headings[0].textContent?.trim();
        if (firstHeading && firstHeading.length > 0) {
          return firstHeading;
        }
      }

      // If no heading found, try to extract from markdown-style headers
      const textContent = element.textContent || '';
      const lines = textContent.split('\n');

      for (const line of lines) {
        const trimmedLine = line.trim();
        // Check for markdown headers (# ## ### etc.)
        if (trimmedLine.match(/^#{1,6}\s+(.+)$/)) {
          const headerText = trimmedLine.replace(/^#{1,6}\s+/, '').trim();
          if (headerText.length > 0) {
            return headerText;
          }
        }
        // Check for lines that look like titles (longer than 10 chars, no common sentence patterns)
        if (trimmedLine.length > 10 && trimmedLine.length < 100 &&
            !trimmedLine.includes('。') && !trimmedLine.includes('.') &&
            !trimmedLine.includes('，') && !trimmedLine.includes(',') &&
            (trimmedLine.includes('报告') || trimmedLine.includes('分析') ||
             trimmedLine.includes('研究') || trimmedLine.includes('Report') ||
             trimmedLine.includes('Analysis') || trimmedLine.includes('Study'))) {
          return trimmedLine;
        }
      }

      // Fallback to default title
      return title;
    };

    const extractedTitle = extractTitle(clonedElement);
    console.log('📋 Extracted title:', extractedTitle);

    // Debug: Check if content contains Chinese characters
    console.log('🔍 Original element content preview:', element.textContent?.substring(0, 200));
    console.log('🔍 Cloned element content preview:', clonedElement.textContent?.substring(0, 200));
    console.log('🔍 Contains Chinese characters:', /[\u4e00-\u9fff]/.test(clonedElement.textContent || ''));

    // Create clean HTML for the new window
    const windowHTML = `
      <!DOCTYPE html>
      <html lang="zh-CN">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${extractedTitle}</title>
          <style>
            body {
              font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", "Helvetica Neue", Arial, sans-serif;
              line-height: 1.6;
              color: #333;
              max-width: 800px;
              margin: 2em auto;
              padding: 2em;
              background: white;
              font-size: 16px;
            }

            h1, h2, h3, h4, h5, h6 {
              color: #000;
              margin-top: 1.5em;
              margin-bottom: 0.5em;
            }

            h1 { font-size: 28px; border-bottom: 2px solid #eee; padding-bottom: 0.5em; }
            h2 { font-size: 24px; }
            h3 { font-size: 20px; }
            h4 { font-size: 18px; }

            p, li {
              margin-bottom: 0.8em;
            }

            ul, ol {
              margin: 1em 0;
              padding-left: 2em;
            }

            blockquote {
              border-left: 4px solid #ddd;
              margin: 1.5em 0;
              padding-left: 1.5em;
              font-style: italic;
              color: #666;
            }

            code {
              background: #f8f9fa;
              padding: 2px 6px;
              border-radius: 4px;
              font-family: "SF Mono", "Monaco", "Menlo", "Source Code Pro", "Consolas", "Liberation Mono", monospace;
              font-size: 0.9em;
            }

            pre {
              background: #f8f9fa;
              padding: 1.5em;
              border-radius: 8px;
              overflow-x: auto;
              border: 1px solid #e9ecef;
              font-family: "SF Mono", "Monaco", "Menlo", "Source Code Pro", "Consolas", "Liberation Mono", monospace;
            }

            pre code {
              background: none;
              padding: 0;
              font-family: inherit;
            }

            table {
              border-collapse: collapse;
              width: 100%;
              margin: 1.5em 0;
              border: 1px solid #ddd;
            }

            th, td {
              border: 1px solid #ddd;
              padding: 12px;
              text-align: left;
            }

            th {
              background: #f8f9fa;
              font-weight: 600;
            }

            /* Hide any buttons or interactive elements */
           

            /* Print styles */
            @media print {
              body {
                margin: 0;
                padding: 1in;
                max-width: none;
              }

              @page {
                margin: 1in;
                size: A4;
              }

              h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
              }

              p, li {
                page-break-inside: avoid;
              }
            }

            .report-header {
              text-align: center;
              margin-bottom: 2em;
              padding-bottom: 1em;
              border-bottom: 2px solid #eee;
            }

            .report-meta {
              color: #666;
              font-size: 0.9em;
              margin-top: 0.5em;
            }

            .report-content {
              margin-top: 2em;
            }

            .print-button {
              position: fixed;
              top: 20px;
              right: 20px;
              background: #007bff;
              color: white;
              border: none;
              padding: 12px 24px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 14px;
              font-weight: 500;
              box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
              transition: all 0.2s ease;
              z-index: 1000;
            }

            .print-button:hover {
              background: #0056b3;
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
            }

            .print-button:active {
              transform: translateY(0);
            }

            /* Hide print button when printing */
            @media print {
              .print-button {
                display: none !important;
              }
            }
          </style>
        </head>
        <body>
          <button class="print-button" onclick="window.print()">🖨️ Print</button>

          <div class="report-header">
            <h1>${extractedTitle}</h1>
            <div class="report-meta">
              Generated on: ${new Date().toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
          <div class="report-content">
            ${clonedElement.innerHTML}
          </div>
        </body>
      </html>
    `;

    // Write content to new window with proper encoding
    newWindow.document.open();
    newWindow.document.write(windowHTML);
    newWindow.document.close();

    // Focus the new window
    newWindow.focus();

    return true;
  } catch (error) {
    console.error('Error opening report window:', error);
    return false;
  }
};

/**
 * Generate filename with timestamp
 */
export const generateFilename = (prefix: string, extension: string): string => {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-');
  return `${prefix}_${timestamp}.${extension}`;
};

/**
 * Clean markdown content for export
 */
export const cleanMarkdownForExport = (content: string, title?: string): string => {
  let cleanContent = content;
  
  // Add title if provided
  if (title) {
    cleanContent = `# ${title}\n\n${cleanContent}`;
  }
  
  // Add metadata
  const metadata = `---
Generated: ${new Date().toISOString()}
Source: Strands DeepSearch Agent
---

`;
  
  cleanContent = metadata + cleanContent;
  
  // Clean up any HTML tags that might be present
  cleanContent = cleanContent.replace(/<[^>]*>/g, '');
  
  // Normalize line endings
  cleanContent = cleanContent.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  
  // Remove excessive blank lines
  cleanContent = cleanContent.replace(/\n{3,}/g, '\n\n');
  
  return cleanContent;
};

/**
 * Export utilities object
 */
export const ExportUtils = {
  exportAsMarkdown,
  exportAsPDF,
  generateFilename,
  cleanMarkdownForExport,
};

export default ExportUtils;
