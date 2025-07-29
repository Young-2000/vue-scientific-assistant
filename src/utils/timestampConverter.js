// 时间戳转换工具

/**
 * 将时间戳转换为可读的日期时间格式
 * @param {number} timestamp - 时间戳（毫秒）
 * @param {string} locale - 地区代码，默认 'zh-CN'
 * @returns {string} 格式化的日期时间字符串
 */
export function formatTimestamp(timestamp, locale = 'zh-CN') {
  if (!timestamp) return '-';
  
  const date = new Date(timestamp);
  return date.toLocaleString(locale);
}

/**
 * 将时间戳转换为相对时间（如：2小时前）
 * @param {number} timestamp - 时间戳（毫秒）
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return '-';
  
  const now = Date.now();
  const diff = now - timestamp;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);
  const years = Math.floor(months / 12);
  
  if (years > 0) return `${years}年前`;
  if (months > 0) return `${months}个月前`;
  if (days > 0) return `${days}天前`;
  if (hours > 0) return `${hours}小时前`;
  if (minutes > 0) return `${minutes}分钟前`;
  if (seconds > 0) return `${seconds}秒前`;
  
  return '刚刚';
}

/**
 * 将时间戳转换为日期字符串（如：2025-07-29）
 * @param {number} timestamp - 时间戳（毫秒）
 * @returns {string} 日期字符串
 */
export function formatDate(timestamp) {
  if (!timestamp) return '-';
  
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

/**
 * 将时间戳转换为时间字符串（如：14:27:46）
 * @param {number} timestamp - 时间戳（毫秒）
 * @returns {string} 时间字符串
 */
export function formatTime(timestamp) {
  if (!timestamp) return '-';
  
  const date = new Date(timestamp);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  
  return `${hours}:${minutes}:${seconds}`;
}

/**
 * 获取时间戳的详细信息
 * @param {number} timestamp - 时间戳（毫秒）
 * @returns {object} 包含各种格式的时间信息
 */
export function getTimestampInfo(timestamp) {
  if (!timestamp) return null;
  
  const date = new Date(timestamp);
  
  return {
    timestamp: timestamp,
    date: date,
    formatted: formatTimestamp(timestamp),
    relative: formatRelativeTime(timestamp),
    dateOnly: formatDate(timestamp),
    timeOnly: formatTime(timestamp),
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate(),
    hours: date.getHours(),
    minutes: date.getMinutes(),
    seconds: date.getSeconds()
  };
}

// 示例：转换您提供的时间戳
export function convertExampleTimestamp() {
  const timestamp = 1753766866243;
  const info = getTimestampInfo(timestamp);
  
  console.log('时间戳转换示例：');
  console.log('原始时间戳:', timestamp);
  console.log('格式化时间:', info.formatted);
  console.log('相对时间:', info.relative);
  console.log('日期:', info.dateOnly);
  console.log('时间:', info.timeOnly);
  console.log('详细信息:', info);
  
  return info;
}

// 如果在浏览器环境中，添加到全局对象
if (typeof window !== 'undefined') {
  window.timestampConverter = {
    formatTimestamp,
    formatRelativeTime,
    formatDate,
    formatTime,
    getTimestampInfo,
    convertExampleTimestamp
  };
} 