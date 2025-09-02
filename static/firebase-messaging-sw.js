// Importa Firebase compat
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// Configuração Firebase
firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

const messaging = firebase.messaging();

// Mensagens em segundo plano
messaging.onBackgroundMessage((payload) => {<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
  import { 
    getAuth, onAuthStateChanged, signOut 
  } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
  import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
  import { 
    getStorage, ref, uploadBytesResumable, getDownloadURL 
  } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-storage.js";
  import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging.js";

  // Config Firebase
  const firebaseConfig = {
    apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
    authDomain: "ecomercie-vendas.firebaseapp.com",
    projectId: "ecomercie-vendas",
    storageBucket: "ecomercie-vendas.firebasestorage.app",
    messagingSenderId: "1054540261609",
    appId: "1:1054540261609:web:90042b823220b4c73f6878",
    measurementId: "G-TNC5M9G89H"
  };

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const db = getFirestore(app);
  const storage = getStorage(app);
  const messaging = getMessaging(app);

  // Gera token FCM
  async function gerarToken() {
    try {
      const token = await getToken(messaging, {
        vapidKey: "BNZLoKzBHSC6kWGUpglcgyo1_xkmS_zmO2ux_VDBEvn5Qai3NJeZfN2u612WVEvMyEao0e1V3rPeReBZVV2nNJg" // 🔑 copie do Firebase Console
      });
      if (token) {
        console.log("🔥 Token FCM:", token);
      } else {
        console.warn("⚠️ Usuário não deu permissão para notificações.");
      }
    } catch (err) {
      console.error("❌ Erro ao gerar token:", err);
    }
  }

  // Receber notificações em primeiro plano
  onMessage(messaging, (payload) => {
    console.log("📩 Notificação recebida:", payload);
    alert(`🔔 ${payload.notification?.title}\n${payload.notification?.body}`);
  });

  // Executa quando abrir painel
  gerarToken();
</script>

  console.log("📩 [SW] Mensagem recebida:", payload);

  const notificationTitle = payload.notification?.title || "Nova notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova mensagem.",
    icon: "/icon-192.png"
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
