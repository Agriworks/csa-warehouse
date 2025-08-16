import React from 'react';

const DashboardPage = () => {
  return (
    <div style={{ width: '100%', height: '100vh', overflow: 'hidden' }}>
      <iframe
        src="https://km-demo-v12.streamlit.app/?embed=true"
        title="Dashboard"
        style={{ width: '100%', height: '100%', border: 'none' }}
        allowFullScreen
      />
    </div>
  );
};

export default DashboardPage;
