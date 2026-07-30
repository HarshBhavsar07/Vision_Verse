// ==================================================
// VisionVerse - Final Unified script.js
// ==================================================

document.addEventListener("DOMContentLoaded", function() {

    // --- 1. IMAGE ANALYSIS LOGIC (Home Page Only) ---
    const imageInput = document.getElementById("imageInput");
    if (imageInput) { 
        const preview = document.getElementById("preview");
        const analyzeBtn = document.getElementById("analyzeBtn");
        const output = document.getElementById("output");
        const customFileLabel = document.querySelector(".custom-file-upload span"); 

        imageInput.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;
            const url = URL.createObjectURL(file);
            preview.src = url;
            preview.style.display = "block";
            customFileLabel.innerText = "Image Selected: " + file.name;
            output.innerHTML = ""; 
        });

        analyzeBtn.addEventListener("click", async function () {
            const file = imageInput.files[0];
            if (!file) return alert("Select an image first!");

            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const img = new Image();
            
            img.onload = async () => {
                const scale = Math.min(1024 / img.width, 1);
                canvas.width = img.width * scale;
                canvas.height = img.height * scale;
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                canvas.toBlob(async (blob) => {
                    const formData = new FormData();
                    formData.append("image", blob, "compressed.webp");

                    output.innerHTML = `
                        <div class="glass-card loading-box">
                            <div class="spinner"></div>
                            <h2>Extracting Intelligence...</h2>
                        </div>`;

                    try {
                        document.getElementById("results").scrollIntoView({ behavior: 'smooth' });
                        const res = await fetch("/analyze", { method: "POST", body: formData });
                        const data = await res.json();

                        if (!res.ok || data.error) throw new Error(data.error || "Analysis Failed");

                        output.innerHTML = `
                            <div class="result-header"><h2>✨ Visual Intelligence Report</h2></div>
                            <div class="ai-grid">
                                <div class="ai-data-card"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>🖼️ Catchy Caption</h3><p>${data.caption}</p></div>
                                <div class="ai-data-card"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>😊 Emotional Mood</h3><p>${data.mood}</p></div>
                                <div class="ai-data-card full-span"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>📝 Description</h3><p>${data.description}</p></div>
                                <div class="ai-data-card"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>🌍 Scene</h3><p>${data.scene}</p></div>
                                <div class="ai-data-card"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>📦 Objects</h3><p>${data.objects}</p></div>
                                <div class="ai-data-card"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>📸 Instagram</h3><p>${data.instagram}</p></div>
                                <div class="ai-data-card"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>#️⃣ Hashtags</h3><p style="color:#4CC9F0">${data.hashtags}</p></div>
                                <div class="ai-data-card full-span"><button class="copy-btn" onclick="copyCardText(this)">📋</button><h3>💡 Thought</h3><p><em>"${data.creative}"</em></p></div>
                            </div>`;
                    } catch (e) {
                        output.innerHTML = `<div class="glass-card" style="border-left:5px solid #ff4757"><h2>❌ Error</h2><p>${e.message}</p></div>`;
                    }
                }, "image/webp", 0.6);
            };
            img.src = URL.createObjectURL(file);
        });

        if (window.location.pathname === '/') {
            fetch('/get_profile')
            .then(response => response.json())
            .then(data => {
                if(data.name) {
                    const pName = document.getElementById('p_name');
                    if (pName) {
                        pName.innerText = data.name;
                        document.getElementById('p_email').innerText = data.email;
                        document.getElementById('p_phone').innerText = data.phone;
                    }
                }
            })
            .catch(err => console.error("Profile load nahi hua:", err));
        }
    }
});

// --- 2. AUTH LOGIC ---
window.switchTab = function(type) {
    const lForm = document.getElementById('login-form');
    const sForm = document.getElementById('signup-form');
    if(!lForm || !sForm) return;

    lForm.style.display = type === 'login' ? 'block' : 'none';
    sForm.style.display = type === 'signup' ? 'block' : 'none';
    document.getElementById('lTab').classList.toggle('active', type === 'login');
    document.getElementById('sTab').classList.toggle('active', type === 'signup');
}

window.authAction = async function(type) {
    if (type === 'signup') {
        const pass = document.getElementById('s_pass').value;
        const cpass = document.getElementById('s_cpass').value;
        const errorMsg = document.getElementById('password-error');

        // Validation Check
        if (pass !== cpass) {
            if (errorMsg) errorMsg.style.display = 'block';
            else alert("Passwords do not match!");
            return;
        }
        if (errorMsg) errorMsg.style.display = 'none';

        const res = await fetch('/signup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: document.getElementById('s_name').value,
                email: document.getElementById('s_email').value,
                phone: document.getElementById('s_phone').value,
                password: pass
            })
        });
        if(res.ok) { alert("Registered!"); switchTab('login'); }
        else alert("Signup Failed!");
    } else {
        const res = await fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                phone: document.getElementById('l_phone').value,
                password: document.getElementById('l_pass').value
            })
        });
        if(res.ok) window.location.href = "/";
        else alert("Login Failed!");
    }
}

// --- 3. PROFILE TOGGLE & COPY ---
window.toggleProfile = function() {
    const box = document.getElementById('profileBox');
    if(box) box.style.display = (box.style.display === 'none' || box.style.display === '') ? 'block' : 'none';
};

window.copyCardText = function(button) {
    const card = button.parentElement;
    const text = `${card.querySelector('h3').innerText}\n${card.querySelector('p').innerText}`;
    navigator.clipboard.writeText(text);
    button.innerText = "✅";
    setTimeout(() => button.innerText = "📋", 2000);
};