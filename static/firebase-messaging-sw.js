// Service Worker para FCM
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// Configuração do seu projeto Firebase
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

// 👉 Recebe notificações em segundo plano (quando app está fechado ou não focado)
messaging.onBackgroundMessage(function(payload) {
  console.log("📩 [SW] Mensagem recebida em segundo plano:", payload);

  const notificationTitle = payload.notification?.title || "Nova Notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova mensagem.",
    icon: "/icon-192.png" // usa seu ícone PWA
  };

  // Mostra notificação no celular/desktop
  self.registration.showNotification(notificationTitle, notificationOptions);
});
