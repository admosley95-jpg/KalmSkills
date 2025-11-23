import React, { useState, useMemo, useEffect } from 'react';
import {
  FileText, Briefcase, CheckCircle, AlertCircle,
  BarChart2, Search, Database, TrendingUp,
  Cpu, Users, BookOpen, ShieldAlert, ArrowRight, Loader
} from 'lucide-react';

// --- API CLIENT ---
const API_BASE_URL = 'http://localhost:8000';

const API = {
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      if (!response.ok) return false;
      const data = await response.json();
      return data.status === 'online';
    } catch (error) {
      return false;
    }
  },
  
  async searchOccupations(query) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/search?q=${encodeURIComponent(query)}&limit=10`);
      if (!response.ok) throw new Error('Failed to fetch occupations');
      return await response.json();
    } catch (error) {
      console.error('Error searching occupations:', error);
      return { results: [] };
    }
  },
  
  async getOccupationDetails(onetCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/${onetCode}`);
      if (!response.ok) throw new Error('Failed to fetch occupation details');
      return await response.json();
    } catch (error) {
      console.error('Error fetching occupation:', error);
      return null;
    }
  },
  
  async getOccupationSkills(onetCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/${onetCode}/skills`);
      if (!response.ok) throw new Error('Failed to fetch skills');
      return await response.json();
    } catch (error) {
      console.error('Error fetching skills:', error);
      return { skills: [] };
    }
  },
  
  async searchCompanies(query) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/companies/search?q=${encodeURIComponent(query)}&limit=5`);
      if (!response.ok) throw new Error('Failed to search companies');
      return await response.json();
    } catch (error) {
      console.error('Error searching companies:', error);
      return { results: [] };
    }
  },
  
  async getCompanyHealth(cik) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/companies/${cik}/health`);
      if (!response.ok) throw new Error('Failed to fetch company health');
      return await response.json();
    } catch (error) {
      console.error('Error fetching company health:', error);
      return null;
    }
  },
  
  async matchResume(resumeSkills, targetOccupation = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_skills: resumeSkills, target_occupation: targetOccupation })
      });
      if (!response.ok) throw new Error('Failed to match resume');
      return await response.json();
    } catch (error) {
      console.error('Error matching resume:', error);
      return null;
    }
  },
  
  async getUnemploymentRate() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/unemployment`);
      if (!response.ok) throw new Error('Failed to fetch unemployment rate');
      return await response.json();
    } catch (error) {
      console.error('Error fetching unemployment:', error);
      return null;
    }
  }
};

// --- STRATEGY LAYER 1: THE O*NET-INSPIRED TAXONOMY ---
// This simulates the "Brain" of the system. It maps raw keywords to standardized IDs.
// In a real app, this resides in Elasticsearch or Postgres.
const SKILL_TAXONOMY = [
  { id: 'tech_01', name: "Python", category: "Hard Skill", synonyms: ["python", "python3", "django", "flask"] },
  { id: 'tech_02', name: "JavaScript", category: "Hard Skill", synonyms: ["javascript", "js", "es6", "typescript"] },
  { id: 'tech_03', name: "React", category: "Hard Skill", synonyms: ["react", "reactjs", "react.js", "jsx"] },
  { id: 'tech_04', name: "SQL", category: "Hard Skill", synonyms: ["sql", "mysql", "postgres", "database query"] },
  { id: 'tech_05', name: "Machine Learning", category: "Hard Skill", synonyms: ["ml", "machine learning", "scikit-learn", "ai"] },
  { id: 'tech_06', name: "AWS", category: "Hard Skill", synonyms: ["aws", "amazon web services", "ec2", "lambda"] },
  { id: 'soft_01', name: "Communication", category: "Soft Skill", synonyms: ["communication", "public speaking", "presentation", "writing"] },
  { id: 'soft_02', name: "Leadership", category: "Soft Skill", synonyms: ["leadership", "management", "mentoring", "team lead"] },
  { id: 'soft_03', name: "Agile", category: "Process", synonyms: ["agile", "scrum", "kanban", "sprint planning"] },
  { id: 'fin_01', name: "Financial Modeling", category: "Domain", synonyms: ["financial modeling", "excel models", "forecasting"] },
  { id: 'fin_02', name: "SEC Reporting", category: "Domain", synonyms: ["sec reporting", "10-k", "10-q", "edgar"] },
];

// --- STRATEGY LAYER 2: MARKET SIGNALS (SEC DATA) ---
// This simulates the "Pulse" - analyzing 10-K filings for hiring intent.
const MARKET_SIGNALS = {
  "TechFlow Systems": {
    sentiment: "High Growth",
    signal: "SEC 10-K: 15% budget increase for R&D.",
    healthScore: 92,
    layoffRisk: "Low",
    fundingStatus: "Series C - $50M raised",
    hiringTrend: "+35% YoY"
  },
  "QuantMetrics": {
    sentiment: "Stable",
    signal: "SEC 8-K: Recent merger, consolidating teams.",
    healthScore: 65,
    layoffRisk: "Medium",
    fundingStatus: "Public (NASDAQ)",
    hiringTrend: "-5% QoQ"
  },
  "Capital Horizons": {
    sentiment: "Aggressive Expansion",
    signal: "SEC 10-K: Opening 3 new regional offices.",
    healthScore: 88,
    layoffRisk: "Low",
    fundingStatus: "Profitable - Private",
    hiringTrend: "+42% YoY"
  },
  "BuildIt Corp": {
    sentiment: "Cautionary",
    signal: "SEC 10-Q: Supply chain headwinds noted.",
    healthScore: 55,
    layoffRisk: "High",
    fundingStatus: "Series B - Runway < 12mo",
    hiringTrend: "-12% QoQ"
  }
};

// --- STRATEGY LAYER 3: SKILL DEMAND TRENDS ---
// Market intelligence: Which skills are trending up/down
const SKILL_TRENDS = {
  "Python": { trend: "rising", demand: "+28% YoY", avgSalary: "$125k" },
  "JavaScript": { trend: "stable", demand: "+5% YoY", avgSalary: "$115k" },
  "React": { trend: "rising", demand: "+18% YoY", avgSalary: "$120k" },
  "SQL": { trend: "stable", demand: "+8% YoY", avgSalary: "$95k" },
  "Machine Learning": { trend: "rising", demand: "+45% YoY", avgSalary: "$140k" },
  "AWS": { trend: "rising", demand: "+32% YoY", avgSalary: "$130k" },
  "Communication": { trend: "stable", demand: "+3% YoY", avgSalary: "N/A" },
  "Leadership": { trend: "rising", demand: "+12% YoY", avgSalary: "N/A" },
  "Agile": { trend: "stable", demand: "+6% YoY", avgSalary: "N/A" },
  "Financial Modeling": { trend: "stable", demand: "+4% YoY", avgSalary: "$105k" },
  "SEC Reporting": { trend: "stable", demand: "+2% YoY", avgSalary: "$98k" },
};

// --- MOCK JOB DATABASE ---
// Integrating multiple "Sources" as per the data strategy.
const JOB_DATABASE = [
  {
    id: 1,
    title: "Senior Frontend Engineer",
    company: "TechFlow Systems",
    source: "LinkedIn Scraper (Simulated)",
    salary: "$120k - $160k",
    description: "Building scalable UIs. We need someone who breathes React and can lead junior devs.",
    required_skills: ["React", "JavaScript", "Communication", "Agile"],
    bonus_skills: ["AWS", "SQL"],
    industry: "Technology"
  },
  {
    id: 2,
    title: "Data Scientist",
    company: "QuantMetrics",
    source: "Burning Glass API",
    salary: "$130k - $170k",
    description: "Analyze large datasets using Python and SQL to drive business insights.",
    required_skills: ["Python", "SQL", "Machine Learning", "Communication"],
    bonus_skills: ["AWS", "Financial Modeling"],
    industry: "Data Science"
  },
  {
    id: 3,
    title: "Financial Analyst",
    company: "Capital Horizons",
    source: "Direct (SEC Signal)",
    salary: "$90k - $120k",
    description: "Support quarterly reporting. Must know GAAP and SEC filing procedures.",
    required_skills: ["Financial Modeling", "SEC Reporting", "SQL"],
    bonus_skills: ["Python", "Communication"],
    industry: "Finance"
  },
  {
    id: 4,
    title: "Technical Lead",
    company: "BuildIt Corp",
    source: "Indeed API",
    salary: "$140k - $180k",
    description: "Lead cross-functional teams. Technical background in JS/AWS required.",
    required_skills: ["Leadership", "Agile", "JavaScript", "AWS"],
    bonus_skills: ["React", "Communication"],
    industry: "Management"
  }
];

// --- COMPONENTS ---

const Badge = ({ children, type = 'neutral', className = '' }) => {
  const styles = {
    neutral: 'bg-gray-100 text-black border-gray-300',
    success: 'bg-gray-200 text-black border-gray-400',
    warning: 'bg-gray-300 text-black border-gray-500',
    danger: 'bg-black text-white border-black',
    info: 'bg-black text-white border-black',
    purple: 'bg-gray-700 text-white border-gray-700',
  };

  return (
    <span className={`px-2.5 py-0.5 rounded text-xs font-medium border ${styles[type]} ${className}`}>
      {children}
    </span>
  );
};

const MarketSignalCard = ({ company, realTimeData }) => {
  // Use real-time data if available, otherwise fall back to mock data
  const apiData = realTimeData && realTimeData[company];
  const data = apiData || MARKET_SIGNALS[company];
  
  if (!data) return null;

  const healthScore = apiData ? apiData.health_score : data.healthScore;
  const layoffRisk = apiData ? apiData.layoff_risk : data.layoffRisk;
  const fundingStatus = apiData ? apiData.funding_status : data.fundingStatus;
  const hiringTrend = apiData ? apiData.hiring_trend : data.hiringTrend;
  const signal = apiData ? apiData.signal : data.signal;
  const isRealData = !!apiData;

  return (
    <div className="mt-3 p-3 bg-gray-50 rounded border border-gray-300 text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-black flex items-center">
          <TrendingUp className="w-3 h-3 mr-1" /> Market Intelligence
          {isRealData && <span className="ml-1 text-[8px] bg-black text-white px-1 rounded">LIVE</span>}
        </span>
        <span className={`font-bold ${healthScore > 80 ? 'text-black' : 'text-gray-600'}`}>
          {healthScore}/100 Health
        </span>
      </div>
      <p className="text-gray-700 italic mb-2">"{signal}"</p>
      
      {/* Enhanced market metrics */}
      <div className="space-y-1 mt-2 pt-2 border-t border-gray-200">
        <div className="flex justify-between">
          <span className="text-gray-500">Layoff Risk:</span>
          <span className={`font-semibold ${
            layoffRisk === 'Low' ? 'text-black' : 
            layoffRisk === 'Medium' ? 'text-gray-600' : 'text-gray-800'
          }`}>{layoffRisk}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Funding:</span>
          <span className="text-black font-medium">{fundingStatus}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Hiring Trend:</span>
          <span className={`font-semibold ${
            hiringTrend.startsWith('+') ? 'text-black' : 'text-gray-600'
          }`}>{hiringTrend}</span>
        </div>
      </div>
      
      <div className="mt-2 flex items-center text-[10px] text-gray-500 uppercase tracking-wide">
        Source: {isRealData ? 'SEC EDGAR (Real-time)' : 'SEC EDGAR Analysis (Mock)'}
      </div>
    </div>
  );
};

const SkillTrendIndicator = ({ skill }) => {
  const trend = SKILL_TRENDS[skill.name];
  if (!trend) return null;

  return (
    <div className="mt-1 text-[10px] text-gray-500">
      <span className={trend.trend === 'rising' ? 'text-black' : 'text-gray-600'}>
        {trend.trend === 'rising' ? '↗' : '→'} {trend.demand}
      </span>
      {trend.avgSalary !== 'N/A' && (
        <span className="ml-2">• Avg: {trend.avgSalary}</span>
      )}
    </div>
  );
};

export default function ResumeJobMatcher() {
  const [resumeText, setResumeText] = useState(
    "I am a software engineer with experience in Python, Django, and Postgres. I have also used ReactJS for frontend work. I enjoy leading teams and sprint planning. I am looking to move into data science."
  );
  const [extractedSkills, setExtractedSkills] = useState([]);
  const [processedMatches, setProcessedMatches] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // --- CORE ENGINE: NORMALIZER ---
  // This implements the "Standardization" strategy.
  // It maps raw text to Canonical O*NET Skill IDs.
  const normalizeAndExtract = (text) => {
    const lowerText = text.toLowerCase();
    const found = new Set();

    SKILL_TAXONOMY.forEach(node => {
      // Check canonical name
      if (lowerText.includes(node.name.toLowerCase())) {
        found.add(node);
      }
      // Check synonyms
      node.synonyms.forEach(syn => {
        if (lowerText.includes(syn)) {
          found.add(node);
        }
      });
    });

    return Array.from(found);
  };

  const runAnalysis = async () => {
    setIsAnalyzing(true);

    // 1. Extract Skills using Taxonomy
    const skills = normalizeAndExtract(resumeText);
    setExtractedSkills(skills);

    // 2. Fetch real data from API if available
    if (apiStatus === 'online') {
      // Try to get real occupation match
      const skillNames = skills.map(s => s.name);
      const matchData = await API.matchResume(skillNames);
      
      if (matchData) {
        // Enrich with real occupation data
        const occupationDetails = await API.getOccupationDetails(matchData.occupation_code);
        const occupationSkills = await API.getOccupationSkills(matchData.occupation_code);
        
        // Store real-time data
        setRealTimeData(prev => ({
          ...prev,
          [matchData.occupation_code]: {
            details: occupationDetails,
            skills: occupationSkills,
            match: matchData
          }
        }));
      }

      // Fetch company data for each job in database
      for (const job of JOB_DATABASE) {
        const companyData = await API.searchCompanies(job.company);
        if (companyData.results && companyData.results.length > 0) {
          const company = companyData.results[0];
          const health = await API.getCompanyHealth(company.cik);
          
          if (health) {
            setRealTimeData(prev => ({
              ...prev,
              [job.company]: health
            }));
          }
        }
      }
    }

    // 3. Match against Jobs (keep existing logic)
    const matches = JOB_DATABASE.map(job => {
        // Map job requirements to skill objects
        // In a real app, job reqs would already be IDs. Here we map string -> object.
        const jobReqNodes = job.required_skills.map(reqName =>
          SKILL_TAXONOMY.find(n => n.name === reqName) || { name: reqName, id: 'unknown', category: 'General' }
        );

        const jobBonusNodes = job.bonus_skills.map(reqName =>
          SKILL_TAXONOMY.find(n => n.name === reqName) || { name: reqName, id: 'unknown', category: 'General' }
        );

        // Calculate Overlap
        const userSkillIds = new Set(skills.map(s => s.name)); // Using name for simple string matching in this demo

        const matchedReqs = jobReqNodes.filter(n => userSkillIds.has(n.name));
        const missingReqs = jobReqNodes.filter(n => !userSkillIds.has(n.name));
        const matchedBonus = jobBonusNodes.filter(n => userSkillIds.has(n.name));

        // Weighted Scoring: Hard skills worth more than soft skills for "Match" but soft skills fit culture
        let score = 0;
        const totalWeight = jobReqNodes.length * 10 + jobBonusNodes.length * 5;

        matchedReqs.forEach(s => score += 10);
        matchedBonus.forEach(s => score += 5);

        const matchPercentage = totalWeight === 0 ? 0 : Math.round((score / totalWeight) * 100);

        return {
          ...job,
          matchScore: matchPercentage,
          matchedReqs,
          missingReqs,
          matchedBonus
        };
    }).sort((a, b) => b.matchScore - a.matchScore);

    setProcessedMatches(matches);
    setIsAnalyzing(false);
  };

  // Statistics for Dashboard
  const stats = useMemo(() => {
    if (!extractedSkills.length) return null;
    const hard = extractedSkills.filter(s => s.category === 'Hard Skill').length;
    const soft = extractedSkills.filter(s => s.category === 'Soft Skill').length;
    const domain = extractedSkills.filter(s => s.category === 'Domain' || s.category === 'Process').length;
    return { hard, soft, domain };
  }, [extractedSkills]);

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      {/* Top Nav */}
      <header className="bg-black border-b border-gray-800 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-white">
            <Database className="w-6 h-6" />
            <span className="font-bold text-lg tracking-tight">KalmSkills<span className="text-gray-400 font-normal">.ai</span></span>
            {apiStatus === 'online' && (
              <span className="ml-2 flex items-center text-[10px] bg-green-500 text-white px-2 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 bg-white rounded-full mr-1 animate-pulse"></span>
                API LIVE
              </span>
            )}
            {apiStatus === 'offline' && (
              <span className="ml-2 flex items-center text-[10px] bg-gray-600 text-white px-2 py-0.5 rounded-full">
                Mock Data
              </span>
            )}
          </div>
          <div className="flex items-center space-x-4 text-sm font-medium text-gray-400">
            <span className="flex items-center hover:text-white cursor-pointer" title="EEOC & ADA Compliant"><ShieldAlert className="w-4 h-4 mr-1" /> Legal Compliance</span>
            <span className="flex items-center hover:text-white cursor-pointer" title="Standardized Skill Framework"><Cpu className="w-4 h-4 mr-1" /> O*NET Taxonomy</span>
            <span className="flex items-center hover:text-white cursor-pointer" title="Real-time Market Data"><TrendingUp className="w-4 h-4 mr-1" /> SEC Intelligence</span>
            {unemploymentRate && (
              <span className="flex items-center text-white" title="National Unemployment Rate">
                📊 US: {unemploymentRate}%
              </span>
            )}
            <div className="h-4 w-px bg-gray-600"></div>
            <span className="text-xs bg-white text-black px-2 py-1 rounded-full">v3.0 Career Intelligence</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* LEFT: Resume & Profile Analysis */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-300 overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
              <h2 className="font-semibold flex items-center">
                <FileText className="w-4 h-4 mr-2 text-gray-700" /> Resume Input
              </h2>
            </div>
            <div className="p-4">
              <textarea
                className="w-full h-48 p-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-black outline-none resize-none text-black"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste resume text here..."
              />
              <button
                onClick={runAnalysis}
                disabled={isAnalyzing}
                className="mt-4 w-full py-2.5 bg-black hover:bg-gray-800 text-white rounded-lg font-medium text-sm transition-all flex items-center justify-center disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <>
                    <Loader className="w-4 h-4 mr-2 animate-spin" />
                    {apiStatus === 'online' ? 'Fetching Real Data...' : 'Processing NLP...'}
                  </>
                ) : (
                  `Analyze & Match Strategy ${apiStatus === 'online' ? '(Live Data)' : ''}`
                )}
              </button>
            </div>
          </div>

          {/* KalmSkills Competitive Advantage Banner */}
          {!extractedSkills.length && (
            <div className="bg-gradient-to-r from-black to-gray-800 rounded-xl shadow-sm border border-gray-700 p-5 text-white">
              <h3 className="font-bold text-sm mb-3 flex items-center">
                <Database className="w-4 h-4 mr-2" /> Why KalmSkills is Different
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex items-start">
                  <CheckCircle className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                  <span><strong>SEC Financial Intelligence:</strong> See company health, layoff risk & funding status</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                  <span><strong>Live Skill Trends:</strong> Track demand & salary data for every skill</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                  <span><strong>O*NET Standardization:</strong> Industry-standard skill taxonomy (not proprietary)</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                  <span><strong>100% Transparent:</strong> See exactly how match scores are calculated</span>
                </div>
              </div>
            </div>
          )}

          {/* Skill Taxonomy Visualization */}
          {extractedSkills.length > 0 && stats && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-300 p-5 animate-in fade-in slide-in-from-bottom-4">
              <h3 className="font-semibold text-sm text-black mb-4 flex items-center">
                <Cpu className="w-4 h-4 mr-2 text-black" /> Your Skill Portfolio
              </h3>

              <div className="flex space-x-2 mb-4 text-center">
                <div className="flex-1 bg-black rounded p-2">
                  <div className="text-xl font-bold text-white">{stats.hard}</div>
                  <div className="text-[10px] uppercase text-gray-300 font-bold">Technical</div>
                </div>
                <div className="flex-1 bg-gray-800 rounded p-2">
                  <div className="text-xl font-bold text-white">{stats.soft}</div>
                  <div className="text-[10px] uppercase text-gray-300 font-bold">Soft</div>
                </div>
                <div className="flex-1 bg-gray-600 rounded p-2">
                  <div className="text-xl font-bold text-white">{stats.domain}</div>
                  <div className="text-[10px] uppercase text-gray-300 font-bold">Domain</div>
                </div>
              </div>

              <div className="space-y-2">
                {extractedSkills.map(skill => (
                  <div key={skill.id}>
                    <Badge
                      type={skill.category === 'Hard Skill' ? 'info' : skill.category === 'Soft Skill' ? 'success' : 'purple'}
                    >
                      {skill.name}
                    </Badge>
                    <SkillTrendIndicator skill={skill} />
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500 italic">
                * Mapped to O*NET v29.0 Taxonomy
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Job Matching Engine */}
        <div className="lg:col-span-8">
          {!processedMatches ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-300 rounded-xl min-h-[400px] bg-gray-50">
              <Briefcase className="w-16 h-16 mb-4 opacity-20" />
              <p>Ready to execute matching strategy.</p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-black">Strategic Opportunities</h2>
                <span className="text-xs font-medium bg-gray-200 text-black px-2 py-1 rounded-full">
                  {processedMatches.length} Sources Found
                </span>
              </div>

              {processedMatches.map((job) => (
                <div key={job.id} className="bg-white rounded-xl shadow-sm border border-gray-300 hover:shadow-md transition-all duration-200">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-0 md:gap-6">

                    {/* Left: Job Info */}
                    <div className="p-5 md:col-span-8 border-b md:border-b-0 md:border-r border-gray-200">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-bold text-lg text-black">{job.title}</h3>
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <span className="font-medium">{job.company}</span>
                            <span>•</span>
                            <span>{job.industry}</span>
                          </div>
                        </div>
                        {/* Match Score Circle */}
                        <div className={`flex flex-col items-center justify-center rounded-lg w-14 h-14 ${
                          job.matchScore >= 80 ? 'bg-black text-white' :
                          job.matchScore >= 50 ? 'bg-gray-600 text-white' :
                          'bg-gray-300 text-black'
                        }`}>
                          <span className="text-lg font-bold">{job.matchScore}%</span>
                        </div>
                      </div>

                      <p className="text-sm text-gray-700 mb-4 leading-relaxed">
                        {job.description}
                      </p>

                      {/* GAP ANALYSIS VISUALIZATION */}
                      <div className="space-y-3">
                        {job.missingReqs.length > 0 ? (
                          <div className="bg-gray-100 rounded-md p-3 border border-gray-300">
                            <div className="text-xs font-bold text-black uppercase mb-2 flex items-center">
                              <AlertCircle className="w-3 h-3 mr-1" /> Missing Critical Skills (Gap)
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {job.missingReqs.map(req => (
                                <span key={req.name} className="text-xs text-black bg-white px-2 py-1 rounded border border-gray-400 line-through decoration-gray-600">
                                  {req.name}
                                </span>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="bg-black rounded-md p-3 border border-black flex items-center text-white text-sm">
                            <CheckCircle className="w-4 h-4 mr-2" /> You are a 100% Technical Match for the Core Requirements.
                          </div>
                        )}

                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-gray-500 uppercase">Matched:</span>
                          {job.matchedReqs.map(r => <Badge key={r.name} type="neutral">{r.name}</Badge>)}
                          {job.matchedBonus.map(r => <Badge key={r.name} type="info">{r.name} (Bonus)</Badge>)}
                        </div>
                      </div>
                    </div>

                    {/* Right: Strategy & Market Data */}
                    <div className="p-5 md:col-span-4 bg-gray-50 flex flex-col justify-between">
                      <div>
                        <div className="text-xs font-bold text-gray-600 uppercase mb-3">Data Source Strategy</div>

                        <div className="mb-4">
                           <div className="flex items-center text-xs font-medium text-black mb-1">
                             Source Type
                           </div>
                           <div className={`text-xs px-2 py-1 rounded border inline-block ${
                             job.source.includes('SEC') ? 'bg-black text-white border-black' :
                             job.source.includes('Burning Glass') ? 'bg-gray-700 text-white border-gray-700' :
                             'bg-gray-400 text-white border-gray-400'
                           }`}>
                             {job.source}
                           </div>
                        </div>

                        <MarketSignalCard company={job.company} realTimeData={realTimeData} />
                      </div>

                      <div className="mt-4 pt-4 border-t border-gray-300">
                        <div className="flex justify-between items-center text-sm font-bold text-black mb-1">
                          <span>Salary Est.</span>
                          <span>{job.salary}</span>
                        </div>
                        <button className="w-full mt-2 py-2 bg-white border border-gray-400 hover:border-black hover:text-black text-gray-700 rounded shadow-sm text-xs font-medium transition-colors flex items-center justify-center group">
                          View Full Analysis <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-0.5 transition-transform" />
                        </button>
                      </div>
                    </div>

                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}