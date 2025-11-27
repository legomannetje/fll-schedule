// GitHub repository info - UPDATE THESE!
const GITHUB_OWNER = 'koenvanwijk';
const GITHUB_REPO = 'ffl-schedule';
const WORKFLOW_FILE = 'schedule.yml';

// GitHub Personal Access Token moet door gebruiker worden ingevoerd
let githubToken = null;

document.getElementById('schedulerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Check if token exists in localStorage
    githubToken = localStorage.getItem('github_token');
    
    if (!githubToken) {
        githubToken = prompt('Enter GitHub Personal Access Token:\n\nGa naar GitHub Settings → Developer settings → Personal access tokens → Generate new token\n\nSelecteer "repo" en "workflow" permissions');
        if (githubToken) {
            localStorage.setItem('github_token', githubToken);
        } else {
            showStatus('GitHub token is nodig om workflow te starten', 'error');
            return;
        }
    }
    
    const formData = {
        num_teams: document.getElementById('numTeams').value,
        num_tables: document.getElementById('numTables').value,
        num_jury_rooms: document.getElementById('numJuryRooms').value,
        matches_per_team: document.getElementById('matchesPerTeam').value,
        num_timeslots: document.getElementById('numTimeslots').value
    };
    
    await triggerWorkflow(formData);
});

async function triggerWorkflow(params) {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Scheduler wordt gestart...';
    
    showStatus('Workflow wordt getriggered...', 'info');
    
    try {
        // Trigger workflow
        const response = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`, {
            method: 'POST',
            headers: {
                'Authorization': `token ${githubToken}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ref: 'main',
                inputs: params
            })
        });
        
        if (response.status === 401) {
            localStorage.removeItem('github_token');
            showStatus('GitHub token is ongeldig. Refresh de pagina en probeer opnieuw.', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = '🚀 Genereer Schema';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showStatus('✅ Workflow gestart! Scheduler draait nu in GitHub Actions...\n\nDit kan 2-5 minuten duren.', 'success');
        
        // Wait a bit for workflow to start
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Poll for workflow run
        await checkWorkflowStatus();
        
    } catch (error) {
        console.error('Error:', error);
        showStatus(`❌ Fout bij starten workflow: ${error.message}`, 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Genereer Schema';
    }
}

async function checkWorkflowStatus() {
    showStatus('⏳ Controleren van workflow status...', 'info');
    
    try {
        // Get latest workflow runs
        const response = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs?per_page=1`, {
            headers: {
                'Authorization': `token ${githubToken}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.workflow_runs.length === 0) {
            showStatus('Geen workflow run gevonden. Check GitHub Actions handmatig.', 'info');
            resetButton();
            return;
        }
        
        const run = data.workflow_runs[0];
        
        if (run.status === 'completed') {
            if (run.conclusion === 'success') {
                showStatus('✅ Schema succesvol gegenereerd!', 'success');
                await downloadArtifact(run.id);
            } else {
                showStatus(`❌ Workflow gefaald: ${run.conclusion}\n\nCheck de logs op GitHub.`, 'error');
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML += `<br><a href="${run.html_url}" target="_blank" class="download-link">📊 Bekijk Logs</a>`;
            }
            resetButton();
        } else if (run.status === 'in_progress' || run.status === 'queued') {
            showStatus(`⏳ Workflow ${run.status}... Check over ${Math.ceil((Date.now() - new Date(run.created_at).getTime()) / 1000 / 60)} min geleden gestart.`, 'info');
            // Poll again in 10 seconds
            setTimeout(checkWorkflowStatus, 10000);
        }
        
    } catch (error) {
        console.error('Error checking status:', error);
        showStatus(`❌ Fout bij controleren status: ${error.message}`, 'error');
        resetButton();
    }
}

async function downloadArtifact(runId) {
    try {
        // Get artifacts for this run
        const response = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}/artifacts`, {
            headers: {
                'Authorization': `token ${githubToken}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.artifacts.length === 0) {
            showStatus('✅ Schema gegenereerd maar artifact niet gevonden.\n\nCheck GitHub Actions artifacts handmatig.', 'info');
            return;
        }
        
        const artifact = data.artifacts[0];
        const statusDiv = document.getElementById('status');
        statusDiv.innerHTML = `✅ Schema succesvol gegenereerd!<br><a href="${artifact.archive_download_url}" class="download-link">📥 Download Schema (.zip)</a><br><small>Note: Download vereist GitHub login</small>`;
        
    } catch (error) {
        console.error('Error downloading artifact:', error);
        showStatus(`✅ Schema gegenereerd!\n\nArtifact download error: ${error.message}\n\nCheck GitHub Actions pagina voor het schema.`, 'success');
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
}

function resetButton() {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = false;
    submitBtn.textContent = '🚀 Genereer Schema';
}
