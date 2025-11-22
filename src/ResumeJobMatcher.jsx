import React, { useState, useMemo, useEffect } from 'react';
import {
  FileText, Briefcase, CheckCircle, AlertCircle,
  BarChart2, Search, Database, TrendingUp,
  Cpu, Users, BookOpen, ShieldAlert, ArrowRight
} from 'lucide-react';

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
    healthScore: 92
  },
  "QuantMetrics": {
    sentiment: "Stable",
    signal: "SEC 8-K: Recent merger, consolidating teams.",
    healthScore: 65
  },
  "Capital Horizons": {
    sentiment: "Aggressive Expansion",
    signal: "SEC 10-K: Opening 3 new regional offices.",
    healthScore: 88
  },
  "BuildIt Corp": {
    sentiment: "Cautionary",
    signal: "SEC 10-Q: Supply chain headwinds noted.",
    healthScore: 55
  }
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
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  };

  return (
    <span className={`px-2.5 py-0.5 rounded text-xs font-medium border ${styles[type]} ${className}`}>
      {children}
    </span>
  );
};

const MarketSignalCard = ({ company }) => {
  const data = MARKET_SIGNALS[company];
  if (!data) return null;

  return (
    <div className="mt-3 p-3 bg-slate-50 rounded border border-slate-200 text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-slate-700 flex items-center">
          <TrendingUp className="w-3 h-3 mr-1" /> Market Intelligence
        </span>
        <span className={`font-bold ${data.healthScore > 80 ? 'text-emerald-600' : 'text-amber-600'}`}>
          {data.healthScore}/100 Health
        </span>
      </div>
      <p className="text-slate-600 italic">"{data.signal}"</p>
      <div className="mt-2 flex items-center text-[10px] text-slate-400 uppercase tracking-wide">
        Source: SEC EDGAR Analysis
      </div>
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

  const runAnalysis = () => {
    setIsAnalyzing(true);

    // Simulate processing time
    setTimeout(() => {
      // 1. Extract Skills using Taxonomy
      const skills = normalizeAndExtract(resumeText);
      setExtractedSkills(skills);

      // 2. Match against Jobs
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
    }, 1200);
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
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Top Nav */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-indigo-700">
            <Database className="w-6 h-6" />
            <span className="font-bold text-lg tracking-tight">SkillGraph<span className="text-slate-400 font-normal">.ai</span></span>
          </div>
          <div className="flex items-center space-x-4 text-sm font-medium text-slate-500">
            <span className="flex items-center hover:text-indigo-600 cursor-pointer"><ShieldAlert className="w-4 h-4 mr-1" /> Legal Compliance</span>
            <span className="flex items-center hover:text-indigo-600 cursor-pointer"><Cpu className="w-4 h-4 mr-1" /> O*NET Taxonomy</span>
            <div className="h-4 w-px bg-slate-300"></div>
            <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full">v2.1 Prototype</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* LEFT: Resume & Profile Analysis */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
              <h2 className="font-semibold flex items-center">
                <FileText className="w-4 h-4 mr-2 text-slate-500" /> Resume Input
              </h2>
            </div>
            <div className="p-4">
              <textarea
                className="w-full h-48 p-3 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none resize-none text-slate-700"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste resume text here..."
              />
              <button
                onClick={runAnalysis}
                disabled={isAnalyzing}
                className="mt-4 w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium text-sm transition-all flex items-center justify-center"
              >
                {isAnalyzing ? 'Processing NLP...' : 'Analyze & Match Strategy'}
              </button>
            </div>
          </div>

          {/* Skill Taxonomy Visualization */}
          {extractedSkills.length > 0 && stats && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 animate-in fade-in slide-in-from-bottom-4">
              <h3 className="font-semibold text-sm text-slate-800 mb-4 flex items-center">
                <Cpu className="w-4 h-4 mr-2 text-indigo-500" /> Standardized Skill Graph
              </h3>

              <div className="flex space-x-2 mb-4 text-center">
                <div className="flex-1 bg-blue-50 rounded p-2">
                  <div className="text-xl font-bold text-blue-700">{stats.hard}</div>
                  <div className="text-[10px] uppercase text-blue-500 font-bold">Technical</div>
                </div>
                <div className="flex-1 bg-emerald-50 rounded p-2">
                  <div className="text-xl font-bold text-emerald-700">{stats.soft}</div>
                  <div className="text-[10px] uppercase text-emerald-500 font-bold">Soft</div>
                </div>
                <div className="flex-1 bg-purple-50 rounded p-2">
                  <div className="text-xl font-bold text-purple-700">{stats.domain}</div>
                  <div className="text-[10px] uppercase text-purple-500 font-bold">Domain</div>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {extractedSkills.map(skill => (
                  <Badge
                    key={skill.id}
                    type={skill.category === 'Hard Skill' ? 'info' : skill.category === 'Soft Skill' ? 'success' : 'purple'}
                  >
                    {skill.name}
                  </Badge>
                ))}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400 italic">
                * Mapped to O*NET v29.0 Taxonomy
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Job Matching Engine */}
        <div className="lg:col-span-8">
          {!processedMatches ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-xl min-h-[400px] bg-slate-50/50">
              <Briefcase className="w-16 h-16 mb-4 opacity-20" />
              <p>Ready to execute matching strategy.</p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900">Strategic Opportunities</h2>
                <span className="text-xs font-medium bg-slate-200 text-slate-600 px-2 py-1 rounded-full">
                  {processedMatches.length} Sources Found
                </span>
              </div>

              {processedMatches.map((job) => (
                <div key={job.id} className="bg-white rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition-all duration-200">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-0 md:gap-6">

                    {/* Left: Job Info */}
                    <div className="p-5 md:col-span-8 border-b md:border-b-0 md:border-r border-slate-100">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-bold text-lg text-indigo-900">{job.title}</h3>
                          <div className="flex items-center space-x-2 text-sm text-slate-600">
                            <span className="font-medium">{job.company}</span>
                            <span>•</span>
                            <span>{job.industry}</span>
                          </div>
                        </div>
                        {/* Match Score Circle */}
                        <div className={`flex flex-col items-center justify-center rounded-lg w-14 h-14 ${
                          job.matchScore >= 80 ? 'bg-emerald-100 text-emerald-700' :
                          job.matchScore >= 50 ? 'bg-amber-100 text-amber-700' :
                          'bg-rose-100 text-rose-700'
                        }`}>
                          <span className="text-lg font-bold">{job.matchScore}%</span>
                        </div>
                      </div>

                      <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                        {job.description}
                      </p>

                      {/* GAP ANALYSIS VISUALIZATION */}
                      <div className="space-y-3">
                        {job.missingReqs.length > 0 ? (
                          <div className="bg-rose-50 rounded-md p-3 border border-rose-100">
                            <div className="text-xs font-bold text-rose-700 uppercase mb-2 flex items-center">
                              <AlertCircle className="w-3 h-3 mr-1" /> Missing Critical Skills (Gap)
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {job.missingReqs.map(req => (
                                <span key={req.name} className="text-xs text-rose-700 bg-white px-2 py-1 rounded border border-rose-200 line-through decoration-rose-400">
                                  {req.name}
                                </span>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="bg-emerald-50 rounded-md p-3 border border-emerald-100 flex items-center text-emerald-800 text-sm">
                            <CheckCircle className="w-4 h-4 mr-2" /> You are a 100% Technical Match for the Core Requirements.
                          </div>
                        )}

                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-slate-400 uppercase">Matched:</span>
                          {job.matchedReqs.map(r => <Badge key={r.name} type="neutral">{r.name}</Badge>)}
                          {job.matchedBonus.map(r => <Badge key={r.name} type="info">{r.name} (Bonus)</Badge>)}
                        </div>
                      </div>
                    </div>

                    {/* Right: Strategy & Market Data */}
                    <div className="p-5 md:col-span-4 bg-slate-50/50 flex flex-col justify-between">
                      <div>
                        <div className="text-xs font-bold text-slate-400 uppercase mb-3">Data Source Strategy</div>

                        <div className="mb-4">
                           <div className="flex items-center text-xs font-medium text-slate-700 mb-1">
                             Source Type
                           </div>
                           <div className={`text-xs px-2 py-1 rounded border inline-block ${
                             job.source.includes('SEC') ? 'bg-purple-100 text-purple-800 border-purple-200' :
                             job.source.includes('Burning Glass') ? 'bg-orange-100 text-orange-800 border-orange-200' :
                             'bg-blue-100 text-blue-800 border-blue-200'
                           }`}>
                             {job.source}
                           </div>
                        </div>

                        <MarketSignalCard company={job.company} />
                      </div>

                      <div className="mt-4 pt-4 border-t border-slate-200">
                        <div className="flex justify-between items-center text-sm font-bold text-slate-800 mb-1">
                          <span>Salary Est.</span>
                          <span>{job.salary}</span>
                        </div>
                        <button className="w-full mt-2 py-2 bg-white border border-slate-300 hover:border-indigo-500 hover:text-indigo-600 text-slate-600 rounded shadow-sm text-xs font-medium transition-colors flex items-center justify-center group">
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