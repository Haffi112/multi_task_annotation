import React, { useEffect, useState } from 'react';

const UserStatus = () => {
  const [taskCounts, setTaskCounts] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTaskCounts = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('/user_task_counts', {
          credentials: 'include',
        });
        if (response.ok) {
          const data = await response.json();
          setTaskCounts(data);
        } else {
          console.error('Failed to fetch task counts');
        }
      } catch (error) {
        console.error('Error fetching task counts:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTaskCounts();
  }, []);

  if (isLoading) return <div>Sæki gögn...</div>;

  return (
    <div style={{ maxWidth: '600px', margin: '20px auto' }}>
      <h2 style={{ marginBottom: '20px', textAlign: 'center' }}>Staða verkefna</h2>
      <ul style={{
        listStyleType: 'none',
        padding: '0',
        margin: '0'
      }}>
        {Object.entries(taskCounts).sort((a, b) => b[1] - a[1]).map(([task, count]) => (
          <li key={task} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '10px',
            padding: '10px',
            border: '1px solid #ccc',
            borderRadius: '8px',
            backgroundColor: '#f9f9f9',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <span style={{ textAlign: 'left', fontSize: '1.2rem' }}>{task}</span>
            <span style={{ textAlign: 'right', fontSize: '1.5rem', fontWeight: 'bold' }}>{count}</span>
          </li>
        ))}
      </ul>
    </div>
)};

export default UserStatus;