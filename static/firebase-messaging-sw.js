// Importa Firebase compatível para SW
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// Config do Firebase
firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

// Inicializa o Messaging
const messaging = firebase.messaging();

// Listener de mensagens em segundo plano
messaging.onBackgroundMessage((payload) => {
  console.log("📩 [SW] Mensagem recebida em segundo plano:", payload);
  const notificationTitle = payload.notification?.title || "Nova notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova mensagem",
    icon: "/icon-192.png"
  };
  self.registration.showNotification(notificationTitle, notificationOptions);
});
