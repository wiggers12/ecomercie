// /static/firebase-init.js
import { firebaseConfig } from "/static/firebase-config.js";

// SDK modular (browser via CDN)
import { initializeApp }   from "https://www.gstatic.com/firebasejs/10.12.3/firebase-app.js";
import { getFirestore }    from "https://www.gstatic.com/firebasejs/10.12.3/firebase-firestore.js";
import { getStorage }      from "https://www.gstatic.com/firebasejs/10.12.3/firebase-storage.js";
// Opcional: Analytics se quiser
// import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.12.3/firebase-analytics.js";

export const app     = initializeApp(firebaseConfig);
export const db      = getFirestore(app);
export const storage = getStorage(app);
// export const analytics = getAnalytics(app); // opcional