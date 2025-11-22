const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'src', 'ResumeJobMatcher.jsx');

try {
  const content = fs.readFileSync(filePath, 'utf8');
  if (content.includes('export default function ResumeJobMatcher')) {
    console.log('Component definition found.');
  } else {
    console.error('Component definition not found.');
    process.exit(1);
  }

  // Basic syntax check (naive)
  try {
    // This won't really parse JSX, but we can check for obvious syntax errors if we had a parser.
    // Since we don't have babel installed, we'll just rely on the file existence and basic string check.
    console.log('File exists and is readable.');
  } catch (e) {
    console.error('Error parsing file:', e);
    process.exit(1);
  }

} catch (err) {
  console.error('Error reading file:', err);
  process.exit(1);
}
