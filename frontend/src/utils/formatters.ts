// Indian number system formatting utilities

/**
 * Formats a number according to the Indian numbering system
 * Examples: 
 * - 1000 -> "1,000"
 * - 100000 -> "1,00,000" (1 lakh)
 * - 10000000 -> "1,00,00,000" (1 crore)
 */
export function formatIndianNumber(num: number): string {
  if (num === 0) return '0';
  
  const numStr = Math.abs(num).toString();
  const isNegative = num < 0;
  
  // For numbers less than 1000, no formatting needed
  if (numStr.length <= 3) {
    return isNegative ? `-${numStr}` : numStr;
  }
  
  // Split into groups according to Indian system
  // Last 3 digits, then groups of 2
  const lastThree = numStr.slice(-3);
  const remaining = numStr.slice(0, -3);
  
  // Add commas every 2 digits from right to left for the remaining part
  const formatted = remaining.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree;
  
  return isNegative ? `-${formatted}` : formatted;
}

/**
 * Converts formatted Indian number string back to number
 * Examples:
 * - "1,00,000" -> 100000
 * - "1,00,00,000" -> 10000000
 */
export function parseIndianNumber(str: string): number {
  if (!str) return 0;
  
  // Remove all commas and convert to number
  const cleaned = str.replace(/,/g, '');
  const num = parseFloat(cleaned);
  
  return isNaN(num) ? 0 : num;
}

/**
 * Formats number with Indian currency and units
 * Examples:
 * - 100000 -> "₹1,00,000 (1 Lakh)"
 * - 10000000 -> "₹1,00,00,000 (1 Crore)"
 */
export function formatIndianCurrency(num: number): string {
  if (num === 0) return '₹0';
  
  const formatted = formatIndianNumber(num);
  let unit = '';
  
  if (num >= 10000000) { // 1 crore or more
    const crores = num / 10000000;
    unit = ` (${crores === 1 ? '1 Crore' : `${formatIndianNumber(Math.floor(crores * 100) / 100)} Crores`})`;
  } else if (num >= 100000) { // 1 lakh or more
    const lakhs = num / 100000;
    unit = ` (${lakhs === 1 ? '1 Lakh' : `${formatIndianNumber(Math.floor(lakhs * 100) / 100)} Lakhs`})`;
  } else if (num >= 1000) { // 1 thousand or more
    const thousands = num / 1000;
    unit = ` (${thousands === 1 ? '1 Thousand' : `${formatIndianNumber(Math.floor(thousands * 100) / 100)} Thousands`})`;
  }
  
  return `₹${formatted}${unit}`;
}

/**
 * Gets placeholder text for income input based on common income ranges
 */
export function getIncomePlaceholder(): string {
  const examples = [
    '2,50,000 (2.5 Lakhs)',
    '5,00,000 (5 Lakhs)', 
    '10,00,000 (10 Lakhs)',
    '25,00,000 (25 Lakhs)'
  ];
  
  return `e.g., ${examples[Math.floor(Math.random() * examples.length)]}`;
}