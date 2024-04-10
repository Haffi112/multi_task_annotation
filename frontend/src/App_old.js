import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  FaBrain, FaRadiation, FaHammer, FaQuestion, FaBalanceScale,
  FaInfoCircle, FaSmileBeam, FaThumbsUp, FaOptinMonster
} from 'react-icons/fa';
import { RiSpam2Fill } from "react-icons/ri";
import './App.css';
import TaskInstructions from './components/TaskInstructions/TaskInstructions';

const tasks = {
  sentiment: ['Positive', 'Negative', 'Neutral'],
  toxicity: ['Toxic', 'Not Toxic'],
  constructive: ['Constructive', 'Not Constructive'],
  offTopic: ['Off-topic', 'On-topic'],
  question: ['Question', 'Not Question'],
  spam: ['Spam', 'Not Spam'],
  debateResponse: ['Agree/Disagree', 'Not a Debate Response'],
  informative: ['Informative/Factual', 'Non-Informative', 'Not Citing Sources'],
  sarcasm: ['Sarcasm/Irony', 'Not Sarcasm/Irony'],
  supportive: ['Supportive/Encouraging', 'Not Supportive/Encouraging'],
  trolling: ['Trolling', 'Not Trolling']
};

const taskIcons = {
  sentiment: FaBrain,
  toxicity: FaRadiation,
  constructive: FaHammer,
  offTopic: FaQuestion,
  question: FaQuestion,
  spam: RiSpam2Fill,
  debateResponse: FaBalanceScale,
  informative: FaInfoCircle,
  sarcasm: FaSmileBeam,
  supportive: FaThumbsUp,
  trolling: FaOptinMonster
};

const debounce = (func, wait) => {
  let timeout;

  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    onLogin(username, password);
  };

  return (
    <div>
      <input type="text" placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

const Logout = ({ onLogout }) => {
  return (
    <button onClick={onLogout}>Logout</button>
  );
};

const Register = ({ onRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleRegister = () => {
    if (!validateEmail(username)) {
      setError('Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }
    setError('');
    onRegister(username, password);
  };

  return (
    <div>
      <input type="text" placeholder="Email" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
      <button onClick={handleRegister}>Register</button>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};


const App = () => {
  const [currentTask, setCurrentTask] = useState(null);
  const [selectedLabels, setSelectedLabels] = useState([]);
  const [currentComment, setCurrentComment] = useState({
    blogPost: {},
    precedingComments: []
  });
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [showBlogPost, setShowBlogPost] = useState(false);
  const [showPrecedingComments, setShowPrecedingComments] = useState(false);

  const navigate = useNavigate();
  const { commentId } = useParams();

  const toggleInstructions = () => {
    setShowInstructions(prev => !prev);
  };

  const toggleDrawer = () => {
    setIsDrawerOpen(prev => !prev);
  };

  const register = async (username, password) => {
    try {
      const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: username, password: password }),
        credentials: 'include',
      });

      if (response.ok) {
        console.log('Registration successful');
        setShowRegister(false);
        login(username, password); // Automatically log in the user after successful registration
      } else {
        console.error('Registration failed');
      }
    } catch (error) {
      console.error('Error during registration:', error);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: username, password: password }),
        credentials: 'include',
      });

      if (response.ok) {
        setLoggedIn(true);
        setUsername(username);
        console.log('Login successful');
      } else {
        console.error('Login failed');
      }
    } catch (error) {
      console.error('Error during login:', error);
    }
  };

  const logout = async () => {
    try {
      const response = await fetch('/logout', {
        method: 'POST',
        credentials: 'include',
      });
  
      if (response.ok) {
        setLoggedIn(false);
        setUsername('');
        console.log('Logout successful');
      } else {
        console.error('Logout failed');
        if (response.status === 401) {
          // Session is expired or user is not logged in, handle as a logout
          handleSessionExpired();
        }
      }
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };
  
  const handleSessionExpired = () => {
    setLoggedIn(false);
    setUsername('');
    // Optionally, redirect to the login page or show a message
    navigate('/'); // Assuming you have a routing setup
    console.log('Session expired. Please log in again.');
  };
  
  // Call this function when the app initializes or when you want to check the session
  const checkLoginStatus = async () => {
    try {
      const response = await fetch('/is_logged_in', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setLoggedIn(data.logged_in);
        if (!data.logged_in) {
          handleSessionExpired();
        }
      }
    } catch (error) {
      console.error('Error checking login status:', error);
    }
  };
  
  useEffect(() => {
    checkLoginStatus();
  }, []);

  const fetchComment = useCallback(async (direction, newTask) => {
    let url = `/annotate?direction=${direction}`;
    if (newTask) {
      url += `&task_type=${currentTask}`;
    } else if (commentId) {
      url += `&current_comment_id=${commentId}`;
    }
  
    try {
      const response = await fetch(url);
      if (response.ok && response.headers.get('Content-Type').includes('application/json')) {
        const data = await response.json();
        setCurrentComment({
          ...data,
          precedingComments: data.preceding_comments,
          blogPost: data.blog_post
        });
        setShowBlogPost(false);
        setShowPrecedingComments(false);
        if (data.comment_id !== commentId) {
          navigate(`/comment/${data.comment_id}`);
        }
      } else {
        console.error('Error fetching comment: Response not OK or not JSON');
        //console.log(response);
        setCurrentComment(null);
      }
    } catch (error) {
      console.error('Error fetching comment:', error);
      setCurrentComment(null);
    }
  }, [commentId, currentTask, navigate]);

  useEffect(() => {
    console.log('Current comment ID:', currentComment?.comment_id);
  }, [currentComment]);

  const isInitialLoad = useRef(true);

  useEffect(() => {
    const init = async () => {
      await checkLoginStatus();
    };
    init();
  }, [checkLoginStatus]);

  useEffect(() => {
    if (commentId && isInitialLoad.current) {
      // Fetch the comment with the given ID from the URL only on initial load
      fetchComment('current', false).catch(console.error);
      isInitialLoad.current = false; // Set to false after initial load
    }
  }, [commentId, fetchComment]);

  const fetchCommentByDirection = debounce((direction) => {
    fetchComment(direction, false);
  }, 300);

  const fetchFirstCommentForTask = useCallback(async (task) => {
    try {
      // Change the URL to point to the next_unannotated endpoint
      const response = await fetch(`/annotate/next_unannotated?task_type=${task}`);
      const data = await response.json();
      if (response.ok) {
        navigate(`/comment/${data.comment_id}`);
        setCurrentComment({
          ...data,
          precedingComments: data.preceding_comments,
          blogPost: data.blog_post
        });
        setShowBlogPost(false);
        setShowPrecedingComments(false);
        console.log('New comment ID:', data.comment_id);
      } else {
        console.error('Error fetching next unannotated comment for task:', task);
        setCurrentComment(null);
      }
    } catch (error) {
      console.error('Error:', error);
      setCurrentComment(null);
    }
  }, [navigate]);

  const fetchUnannotatedComment = useCallback(async (direction) => {
    if (!currentTask) return; // If no task is selected, do nothing

    let url = `/annotate/${direction}_unannotated?task_type=${currentTask}&current_comment_id=${currentComment.comment_id}`;
  
    try {
      const response = await fetch(url);
      if (response.ok && response.headers.get('Content-Type').includes('application/json')) {
        const data = await response.json();
        setCurrentComment({
          ...data,
          precedingComments: data.preceding_comments,
          blogPost: data.blog_post
        });
        setShowBlogPost(false);
        setShowPrecedingComments(false);
        navigate(`/comment/${data.comment_id}`); // Navigate to the new comment's URL
      } else {
        console.error('Failed to fetch unannotated comment:', response.statusText);
      }
     } catch (error) {
      console.error('Error fetching unannotated comment:', error);
    }
  }, [currentTask, currentComment, navigate]);

  const handleTaskSelect = async (task) => {
    setCurrentTask(task);
    setSelectedLabels([]); // Reset label selection

    // Check if a commentId is set or if the current path is '/'
    if (!commentId || window.location.pathname === '/') {
      await fetchFirstCommentForTask(task); // Fetch the next task for the selected type
    }
    // If a commentId is set and the path is not '/', do not fetch a new comment
  };

  const handleLabelSelect = useCallback((label) => {
    if (tasks[currentTask].length > 2) {
      setSelectedLabels(prevLabels => 
        prevLabels.includes(label) ? prevLabels.filter(l => l !== label) : [...prevLabels, label]
      );
    } else {
      setSelectedLabels([label]);
    }
  }, [currentTask]);
  

  const handleSubmit = useCallback(async () => {
    if (selectedLabels.length && currentComment && currentComment.comment_id) {
      const annotationData = {
        commentId: currentComment.comment_id,
        user: username,
        task: currentTask,
        labels: selectedLabels,
      };

      try {
        const response = await fetch('/annotate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(annotationData),
          credentials: 'include'
        });

        if (response.ok) {
          console.log('Annotation submitted successfully');
          // Fetch next comment for this task
          await fetchFirstCommentForTask(currentTask);
        } else {
          console.error('Failed to submit annotation');
          // Handle error
        }
      } catch (error) {
        console.error('Error submitting annotation:', error);
      }
    }
  }, [currentComment, currentTask, fetchFirstCommentForTask, selectedLabels, username]);

  const TaskSelection = ({ currentTask, onTaskSelect }) => {
    return (
      <div className="task-selection">
        {Object.keys(tasks).map((task) => {
          const Icon = taskIcons[task];
          return (
            <button
              key={task}
              onClick={() => onTaskSelect(task)}
              className={currentTask === task ? 'task-button selected' : 'task-button'}
            >
              <Icon /> {task}
            </button>
          );
        })}
      </div>
    );
  };
  
  const LabelSelection = ({ labels, selectedLabels, onLabelSelect }) => {
    const handleLabelClick = (label) => {
      // For multi-label tasks, allow multiple selections
      if (tasks[currentTask].length > 2) {
        setSelectedLabels(prevLabels =>
          prevLabels.includes(label) ? prevLabels.filter(l => l !== label) : [...prevLabels, label]
        );
      } else {
        setSelectedLabels([label]);
      }
    };
  
    return (
      <div className="label-selection">
        {labels.map((label) => (
          <button
            key={label}
            onClick={() => handleLabelClick(label)}
            className={selectedLabels.includes(label) ? 'selected' : ''}
          >
            {label}
          </button>
        ))}
      </div>
    );
  };

  useEffect(() => {
    const handleKeyPress = (event) => {
      // Number keys for label selection
      if (event.key >= '1' && event.key <= '9') {
        const index = parseInt(event.key, 10) - 1; // Convert key to index (1 for 0th index)
        if (currentTask && index < tasks[currentTask].length) {
          handleLabelSelect(tasks[currentTask][index]);
        }
      }

      // Enter key for submission
      if (event.key === 'Enter') {
        handleSubmit();
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [currentTask, handleLabelSelect, handleSubmit]);

  return (
    <div className="App">
      <div className={`auth-top-bar ${isDrawerOpen ? 'expanded' : ''}`}>
        <button className={`hamburger ${loggedIn ? 'logged-in' : ''}`} onClick={toggleDrawer}>
          {isDrawerOpen ? 'Fela verkefnaval' : 'Sýna verkefnaval'}
        </button>
        <div className="auth-controls">
          {!loggedIn && !showRegister && (
            <>
              <Login onLogin={login} />
              <button className="auth-button" onClick={() => setShowRegister(true)}>Register</button>
            </>
          )}
          {!loggedIn && showRegister && <Register onRegister={register} />}
          {loggedIn && (
            <div className="user-section">
              <span className="username">{username}</span>
              <Logout onLogout={logout} />
            </div>
          )}
        </div>
      </div>
      {isDrawerOpen && (
        <TaskSelection currentTask={currentTask} onTaskSelect={handleTaskSelect} />
      )}
      
      {currentComment && (
      <div className="comment-container">
      
        {currentComment && currentComment.blogPost && (
          <div className="blog-post">
            <button className="toggle-button" onClick={() => setShowBlogPost(!showBlogPost)}>
              {showBlogPost ? 'Hide blog' : 'Show blog'}
            </button>
            {showBlogPost && (
              <>
                <h3><a href={currentComment.blogPost.link} target="_blank" rel="noopener noreferrer">{currentComment.blogPost.title}</a></h3>
                <p>{currentComment.blogPost.text}</p>
              </>
            )}
          </div>
        )}
        {currentComment && currentComment.precedingComments && currentComment.precedingComments.length > 0 && (
          <div className="preceding-comments">
            <button className="toggle-button" onClick={() => setShowPrecedingComments(!showPrecedingComments)}>
              {showPrecedingComments ? 'Hide prior comments' : 'Show prior comments'}
            </button>
            {showPrecedingComments && currentComment.precedingComments.map((c) => (
              <div key={c.id} className="preceding-comment">
                <p>{c.text}</p>
                <span className="comment-signature">{c.signature}</span>
              </div>
            ))}
          </div>
        )}
        <div className="current-comment">
          <p>{currentComment.text}</p>
          <span className="comment-signature">{currentComment.signature}</span>
        </div>
        {currentTask && (
          <div className="label-selection-container">
            <LabelSelection labels={tasks[currentTask]} selectedLabels={selectedLabels} onLabelSelect={handleLabelSelect} />
          </div>
        )}
        {currentTask && (<div className="submit-button-container">
          <button onClick={handleSubmit} className="submit-button">
            Submit Annotation
          </button>
        </div>)}
        <div className="navigation-arrows">
          <button onClick={() => fetchUnannotatedComment('previous')} disabled={!currentTask || !currentComment}>&laquo;</button>
          <button onClick={() => fetchCommentByDirection(-1)} disabled={!currentComment}>&larr;</button>
          <button onClick={() => fetchCommentByDirection(1)} disabled={!currentComment}>&rarr;</button>
          <button onClick={() => fetchUnannotatedComment('next')} disabled={!currentTask || !currentComment}>&raquo;</button>
        </div>
        <button onClick={toggleInstructions} className="instructions-toggle-button">
          {showInstructions ? 'Fela leiðbeiningar' : 'Sýna leiðbeiningar'}
        </button>
        {showInstructions && (
          <div className="instructions-container">
            <h2>Leiðbeiningar</h2>
            {currentTask && <TaskInstructions taskName={currentTask} />}
          </div>
        )}
      </div>
    )}
    </div>
  );
};

export default App;
