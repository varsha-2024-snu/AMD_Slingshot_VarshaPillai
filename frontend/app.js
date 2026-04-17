/**
 * app.js — ShopGenie frontend logic
 *
 * Responsibilities:
 * - Firebase Auth: Google Sign-In, token management
 * - API communication: /chat, /vision, /cart routes
 * - Real-time cart badge: Firestore onSnapshot listener
 * - Image upload: client-side validation and base64 encoding
 * - DOM updates: message rendering, product card generation
 * - Accessibility: aria-live updates, focus management
 */

// ─── Configuration ─────────────────────────────────────────────────────────
// Replace with your actual values. These are non-secret — safe in frontend JS.
const FIREBASE_CONFIG = {
  apiKey: "REPLACE_WITH_YOUR_WEB_API_KEY",
  authDomain: "amd-slingshot-cec69.firebaseapp.com",
  projectId: "amd-slingshot-cec69",
  storageBucket: "amd_slingshot",
  messagingSenderId: "REPLACE_WITH_YOUR_SENDER_ID",
  appId: "REPLACE_WITH_YOUR_APP_ID",
};

const API_BASE = window.location.hostname === "localhost"
  ? "http://localhost:8080/api/v1"
  : "https://YOUR_CLOUD_RUN_URL/api/v1";  // This placeholder will be dynamically replaced by deploy.sh

// ─── Firebase Initialisation ────────────────────────────────────────────────
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged }
  from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore, collection, onSnapshot }
  from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const app = initializeApp(FIREBASE_CONFIG);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

// ─── State ───────────────────────────────────────────────────────────────────
let currentUser = null;
let idToken = null;
let pendingImageBase64 = null;
let pendingImageMime = null;
let cartUnsubscribe = null;

// ─── DOM References ───────────────────────────────────────────────────────────
const signInBtn = document.getElementById("sign-in-btn");
const cartBtn = document.getElementById("cart-btn");
const cartBadge = document.getElementById("cart-badge");
const messages = document.getElementById("messages");
const queryInput = document.getElementById("query-input");
const sendBtn = document.getElementById("send-btn");
const uploadBtn = document.getElementById("upload-btn");
const fileInput = document.getElementById("file-input");
const imagePreview = document.getElementById("image-preview");
const removeImageBtn = document.getElementById("remove-image-btn");
const productGrid = document.getElementById("product-grid");
const loading = document.getElementById("loading");
const cartSidebar = document.getElementById("cart-sidebar");
const closeCartBtn = document.getElementById("close-cart-btn");

// ─── Auth ────────────────────────────────────────────────────────────────────
signInBtn.addEventListener("click", async () => {
  if (currentUser) {
    try {
      await signOut(auth);
    } catch (e) {
      appendMessage("system", "Sign-out failed.");
    }
  } else {
    try {
      await signInWithPopup(auth, provider);
    } catch (e) {
      appendMessage("system", "Sign-in failed. Please try again.");
    }
  }
});

onAuthStateChanged(auth, async (user) => {
  currentUser = user;
  if (user) {
    idToken = await user.getIdToken();
    signInBtn.textContent = `Hi, ${user.displayName.split(" ")[0]}`;
    signInBtn.setAttribute("aria-label", `Signed in as ${user.displayName}. Click to sign out.`);
    cartBtn.hidden = false;
    appendMessage("assistant", `Welcome to ShopGenie, ${user.displayName.split(" ")[0]}! 🧞 Tell me what you're looking for, or upload a product photo.`);
    subscribeCartBadge(user.uid);
  } else {
    signInBtn.textContent = "Sign in with Google";
    signInBtn.setAttribute("aria-label", "Sign in with Google");
    cartBtn.hidden = true;
    cartBadge.textContent = "0";
    if (cartUnsubscribe) cartUnsubscribe();
  }
});

// ─── Cart Badge (Firestore real-time) ────────────────────────────────────────
function subscribeCartBadge(uid) {
  if (cartUnsubscribe) cartUnsubscribe();
  const itemsRef = collection(db, "carts", uid, "items");
  cartUnsubscribe = onSnapshot(itemsRef, (snapshot) => {
    let count = 0;
    snapshot.forEach((doc) => {
      count += (doc.data().qty || 0);
    });
    cartBadge.textContent = count;
    cartBadge.setAttribute("aria-label", `${count} items in cart`);
  });
}

// ─── Image Upload ─────────────────────────────────────────────────────────────
uploadBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // Client-side validation — MIME type and 1MB size limit
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    appendMessage("system", "Please upload a JPEG, PNG, or WebP image.");
    return;
  }
  if (file.size > 1 * 1024 * 1024) {
    appendMessage("system", "Image must be under 1MB. Please compress and retry.");
    return;
  }

  const reader = new FileReader();
  reader.onload = (ev) => {
    const dataUrl = ev.target.result;
    pendingImageBase64 = dataUrl.split(",")[1];
    pendingImageMime = file.type;
    // Show preview
    imagePreview.hidden = false;
    imagePreview.querySelector("img").src = dataUrl;
    imagePreview.querySelector("img").alt = `Uploaded image: ${file.name}`;
  };
  reader.readAsDataURL(file);
});

removeImageBtn.addEventListener("click", () => {
  pendingImageBase64 = null;
  pendingImageMime = null;
  imagePreview.hidden = true;
  fileInput.value = "";
});

// ─── Send Message ─────────────────────────────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);
queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

async function sendMessage() {
  if (!currentUser || !idToken) {
    appendMessage("system", "Please sign in to use ShopGenie.");
    return;
  }

  const query = queryInput.value.trim();
  if (!query && !pendingImageBase64) return;

  queryInput.value = "";
  sendBtn.disabled = true;
  setLoading(true);

  if (query) appendMessage("user", query);

  try {
    idToken = await currentUser.getIdToken(); // Refresh token before each request
    let data;
    if (pendingImageBase64) {
      appendMessage("user", "🖼️ [Uploaded image — searching for similar products]");
      data = await callApi("/vision", {
        image_base64: pendingImageBase64,
        mime_type: pendingImageMime,
      });
      removeImageBtn.click(); // Clear image state after sending
    } else {
      data = await callApi("/chat", { query, user_id: currentUser.uid });
    }
    renderResults(data);
  } catch (err) {
    appendMessage("assistant", "⚠️ Something went wrong. Please try again.");
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    setLoading(false);
    queryInput.focus(); // Return focus to input for accessibility
  }
}

async function callApi(path, body) {
  const method = (path === "/cart" && !body.product_id) ? "GET" : "POST";
  const options = {
    method: method,
    headers: { 
      "Content-Type": "application/json", 
      "Authorization": `Bearer ${idToken}` 
    }
  };
  if (method === "POST") options.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error(`API ${path} returned ${res.status}`);
  return res.json();
}

// ─── Render Results ───────────────────────────────────────────────────────────
function renderResults(data) {
  productGrid.innerHTML = "";
  if (data.follow_up) {
    appendMessage("assistant", `🤔 ${data.follow_up}`);
    return;
  }
  if (!data.recommendations || data.recommendations.length === 0) {
    appendMessage("assistant", "I couldn't find a match. Try a different query or upload a photo.");
    return;
  }
  appendMessage("assistant", `Here are my top picks for you:`);
  data.recommendations.forEach((rec) => {
    const card = createProductCard(rec);
    productGrid.appendChild(card);
  });
}

function createProductCard(rec) {
  const card = document.createElement("article");
  card.className = "product-card";
  card.setAttribute("aria-label", `Product: ${rec.name}, ₹${rec.price}`);
  
  // Use a generic placeholder if image_url is missing or as a fallback
  const imgUrl = rec.image_url || "https://placehold.co/400x300?text=Product";
  
  card.innerHTML = `
    <img src="${imgUrl}" alt="${rec.name} — product image" loading="lazy" />
    <h3>${escapeHtml(rec.name)}</h3>
    <p class="price">₹${rec.price.toLocaleString("en-IN")}</p>
    <p class="reason"><em>${escapeHtml(rec.reason)}</em></p>
    <button class="add-to-cart-btn" aria-label="Add ${escapeHtml(rec.name)} to cart"
      data-id="${rec.id}">
      Add to Cart
    </button>`;
  
  card.querySelector(".add-to-cart-btn").addEventListener("click", () => addToCart(rec));
  return card;
}

async function addToCart(rec) {
  if (!currentUser || !idToken) return;
  try {
    idToken = await currentUser.getIdToken();
    await callApi("/cart", { product_id: rec.id, name: rec.name, price: rec.price, qty: 1 });
    // Cart badge updates automatically via Firestore onSnapshot
  } catch (e) {
    appendMessage("system", `Failed to add ${rec.name} to cart.`);
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message message--${role}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight; // Auto-scroll to latest
}

function setLoading(visible) {
  loading.hidden = !visible;
  loading.setAttribute("aria-hidden", visible ? "false" : "true");
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// ─── Cart Sidebar ─────────────────────────────────────────────────────────────
cartBtn.addEventListener("click", async () => {
  if (!currentUser || !idToken) return;
  idToken = await currentUser.getIdToken();
  const data = await callApi("/cart", {});
  
  const contents = document.getElementById("cart-contents");
  contents.innerHTML = "";
  data.items.forEach(item => {
    const itemDiv = document.createElement("div");
    itemDiv.style.margin = "8px 0";
    itemDiv.innerHTML = `${escapeHtml(item.name)} x ${item.qty} - ₹${item.price}`;
    contents.appendChild(itemDiv);
  });
  document.getElementById("cart-total").textContent = `Total: ₹${data.total.toLocaleString("en-IN")}`;
  
  cartSidebar.hidden = false;
  cartSidebar.focus();
});

closeCartBtn.addEventListener("click", () => {
  cartSidebar.hidden = true;
  cartBtn.focus(); // Return focus to trigger element for accessibility
});
