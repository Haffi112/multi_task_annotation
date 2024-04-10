const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  const proxyConfig = createProxyMiddleware({
    target: 'https://localhost:5000',
    changeOrigin: true,
    secure: false,
  });

  ['/login', '/annotate', '/register', '/logout', '/cleanup_test_data', '/leaderboard', '/is_logged_in', '/user_task_counts'].forEach(path => {
    app.use(path, proxyConfig);
  });
};