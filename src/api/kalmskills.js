// API client for KalmSkills Backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class KalmSkillsAPI {
  async searchOccupations(query) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/search?q=${encodeURIComponent(query)}&limit=10`);
      if (!response.ok) throw new Error('Failed to fetch occupations');
      return await response.json();
    } catch (error) {
      console.error('Error searching occupations:', error);
      return { results: [] };
    }
  }

  async getOccupationDetails(onetCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/${onetCode}`);
      if (!response.ok) throw new Error('Failed to fetch occupation details');
      return await response.json();
    } catch (error) {
      console.error('Error fetching occupation:', error);
      return null;
    }
  }

  async getOccupationSkills(onetCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/${onetCode}/skills`);
      if (!response.ok) throw new Error('Failed to fetch skills');
      return await response.json();
    } catch (error) {
      console.error('Error fetching skills:', error);
      return { skills: [] };
    }
  }

  async getTechnologySkills(onetCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/occupations/${onetCode}/technology`);
      if (!response.ok) throw new Error('Failed to fetch technology skills');
      return await response.json();
    } catch (error) {
      console.error('Error fetching tech skills:', error);
      return { technologies: [] };
    }
  }

  async searchCompanies(query) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/companies/search?q=${encodeURIComponent(query)}&limit=5`);
      if (!response.ok) throw new Error('Failed to search companies');
      return await response.json();
    } catch (error) {
      console.error('Error searching companies:', error);
      return { results: [] };
    }
  }

  async getCompanyHealth(cik) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/companies/${cik}/health`);
      if (!response.ok) throw new Error('Failed to fetch company health');
      return await response.json();
    } catch (error) {
      console.error('Error fetching company health:', error);
      return null;
    }
  }

  async getCompanyByTicker(ticker) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/companies/ticker/${ticker}`);
      if (!response.ok) throw new Error('Failed to fetch company');
      return await response.json();
    } catch (error) {
      console.error('Error fetching company:', error);
      return null;
    }
  }

  async getWages(occupationCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/wages/${occupationCode}`);
      if (!response.ok) throw new Error('Failed to fetch wage data');
      return await response.json();
    } catch (error) {
      console.error('Error fetching wages:', error);
      return null;
    }
  }

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

  async matchResume(resumeSkills, targetOccupation = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_skills: resumeSkills,
          target_occupation: targetOccupation
        })
      });
      if (!response.ok) throw new Error('Failed to match resume');
      return await response.json();
    } catch (error) {
      console.error('Error matching resume:', error);
      return null;
    }
  }

  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      if (!response.ok) return false;
      const data = await response.json();
      return data.status === 'online';
    } catch (error) {
      return false;
    }
  }
}

export default new KalmSkillsAPI();
