import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  FaBrain, FaRadiation, FaHammer, FaQuestion, FaBalanceScale,
  FaInfoCircle, FaSmileBeam, FaThumbsUp, FaOptinMonster
} from 'react-icons/fa';
import { RiSpam2Fill } from "react-icons/ri";
import './App.css';
import TaskInstructions from './components/TaskInstructions';
import UserStatus from './components/UserStatus';

const taskIcons = {
  sentiment: FaBrain,
  deepSentiment: FaBrain,
  toxicity: FaRadiation,
  hateSpeech: FaRadiation,
  emotionDetection: FaSmileBeam,
  encouragementAndSympathy: FaThumbsUp,
  constructiveFeedback: FaHammer,
  sarcasmDetection: FaSmileBeam,
  trollDetection: FaOptinMonster
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

const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const Login = React.memo(({ username, password, onLogin, onRegister, setUsername, setPassword, error, setError }) => {

  const handleLogin = () => {
    onLogin(username, password);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  const handleRegister = () => {
    if (!validateEmail(username)) {
      setError('Notendanafnið þarf að vera netfang.');
      return;
    }
    if (password.length < 6) {
      setError('Lykilorð verður að vera a.m.k. 6 stafir.');
      return;
    }
    setError('');
    onRegister(username, password);
  };

  return (
    <div>
      <input type="text" placeholder="Notendanafn" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Lykilorð" onChange={e => setPassword(e.target.value)} onKeyPress={handleKeyPress} />
      <button onClick={handleLogin}>Innskráning</button>
      <button onClick={handleRegister}>Nýskráning</button>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
});

const Logout = ({ onLogout }) => {
  return (
    <button onClick={onLogout}>Útskráning</button>
  );
};


const App = () => {
  const [currentTask, setCurrentTask] = useState(null);
  const [currentTaskFirstName, setCurrentTaskFirstName] = useState(null);
  const [currentComment, setCurrentComment] = useState({
    blogPost: {},
    precedingComments: []
  });
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(''); // Define an error state to manage error messages
  const [showInstructions, setShowInstructions] = useState(false);
  const [showStatus, setShowStatus] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [showBlogPost, setShowBlogPost] = useState(false);
  const [showPrecedingComments, setShowPrecedingComments] = useState(false);
  const [selectedSubtaskTexts, setSelectedSubtaskTexts] = useState({});
  const [selectedSubtaskLabels, setSelectedSubtaskLabels] = useState({});
  const [showToxicitySubtasks, setShowToxicitySubtasks] = useState({
    typeOfToxicity: false,
    targetOfToxicity: false,
  });
  const [showHateSpeechSubtasks, setShowHateSpeechSubtasks] = useState(false);

  useEffect(() => {
    setShowToxicitySubtasks({
      typeOfToxicity: false,
      targetOfToxicity: false,
    });
    setShowHateSpeechSubtasks(false);
  }, [currentTask]);

  const navigate = useNavigate();
  const { commentId } = useParams();

  const toggleInstructions = () => {
    setShowInstructions(prev => !prev);
  };

  const toggleStatus = () => {
    setShowStatus(prev => !prev);
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
  
  const handleSessionExpired = useCallback(() => {
    setLoggedIn(false);
    setUsername('');
    // Optionally, redirect to the login page or show a message
    navigate('/'); // Assuming you have a routing setup
    console.log('Session expired. Please log in again.');
  }, [setLoggedIn, setUsername, navigate]);
  
  const checkLoginStatus = useCallback(async () => {
    try {
      const response = await fetch('/is_logged_in', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setLoggedIn(data.logged_in);
        if (data.logged_in) {
          setUsername(data.username); // Update the username state
        } else {
          handleSessionExpired();
        }
      }
    } catch (error) {
      console.error('Error checking login status:', error);
    }
  }, [handleSessionExpired, setUsername]); // Add setUsername to the dependency array
  
  useEffect(() => {
    checkLoginStatus();
  }, [checkLoginStatus]);

  const fetchComment = useCallback(async (direction, newTask) => {
    let url = `/annotate?direction=${direction}`;
    if (newTask) {
      url += `&task_type=${currentTaskFirstName}`;
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
  }, [commentId, currentTask, currentTaskFirstName, navigate]);

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
          comment_id: data.comment_id,
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

    let url = `/annotate/${direction}_unannotated?task_type=${currentTaskFirstName}&current_comment_id=${currentComment.comment_id}`;
  
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
  }, [currentTask, currentTaskFirstName, currentComment, navigate]);

  const handleTaskSelect = async (taskKey) => {
    const task = tasks[taskKey];
    if (!task) {
      console.error(`Task with key '${taskKey}' not found.`);
      return;
    }
  
    setCurrentTask(taskKey);
    const firstSubtaskKey = Object.keys(tasks[taskKey].subtasks)[0];
    setCurrentTaskFirstName(tasks[taskKey].subtasks[firstSubtaskKey].name);
    setSelectedSubtaskLabels({});
  
    if (!commentId || window.location.pathname === '/') {
      await fetchFirstCommentForTask(currentTaskFirstName); // Fetch the next task for the selected type
    }
  };

  const handleSubmit = useCallback(async () => {
    // Check if all required subtasks have been answered
    const taskData = tasks[currentTask];
    if (!taskData) {
      console.error(`Task with key '${currentTask}' not found.`);
      return;
    }

    const subtaskKeys = Object.keys(taskData.subtasks || {});

    const subtaskKeysToSubmit = subtaskKeys.filter(subtaskKey => {
      if (subtaskKey === 'typeOfToxicity') {
        return showToxicitySubtasks.typeOfToxicity;
      }
      if (subtaskKey === 'targetOfToxicity') {
        return showToxicitySubtasks.targetOfToxicity;
      }
      if (subtaskKey !== 'hateSpeechDetection' && currentTask === 'hateSpeech') {
        return showHateSpeechSubtasks; // Only include hate speech subtasks if they are visible
      }
      return true; // Always include subtasks that don't have visibility conditions
    });

    for (const subtaskKey of subtaskKeysToSubmit) {
      const subtask = taskData.subtasks[subtaskKey];
      const formalName = subtask.name;
      if (subtask.textInput && (!selectedSubtaskTexts[subtaskKey] || selectedSubtaskTexts[subtaskKey].trim() === '')) {
        alert(`Vinsamlegast fylltu út: ${formalName}`);
        return;
      }
      
      // Check if the subtask requires label selection and if it's provided
      if (subtask.labels && (!selectedSubtaskLabels[subtaskKey] || selectedSubtaskLabels[subtaskKey].length === 0)) {
        alert(`Vinsamlegast veldu merkingu fyrir: ${formalName}`);
        return;
      }
    }

    const additionalData = {
        showBlogPost: showBlogPost,
        showPrecedingComments: showPrecedingComments,
    };

    // Prepare the data for each subtask
    const annotationDataList = subtaskKeysToSubmit
      .filter(subtaskKey => {
        return (
          (subtaskKey !== 'typeOfToxicity' || showToxicitySubtasks.typeOfToxicity) &&
          (subtaskKey !== 'targetOfToxicity' || showToxicitySubtasks.targetOfToxicity) &&
          (subtaskKey === 'hateSpeechDetection' || showHateSpeechSubtasks || currentTask !== 'hateSpeech')
        );
      })
      .map(subtaskKey => {
        const subtask = taskData.subtasks[subtaskKey];
        const subtaskName = subtask.name;
        const subtaskData = {
          commentId: currentComment.comment_id,
          user: username,
          task: subtaskName,
          labels: subtask.labels ? selectedSubtaskLabels[subtaskKey].join(';') : selectedSubtaskTexts[subtaskKey],
          additionalData: additionalData
        };
        return subtaskData;
      });

    // Submit all annotation data in parallel
    const submitAllAnnotations = async () => {
      return Promise.all(annotationDataList.map(data => submitAnnotation(data)));
    };

    // Check all responses and fetch the next comment if all submissions were successful
    try {
      const responses = await submitAllAnnotations();
      if (responses.every(response => response.ok)) {
        // Fetch the next unannotated comment for the current task
        await fetchUnannotatedComment('next_submit');
        setSelectedSubtaskTexts({});
        setSelectedSubtaskLabels({});
        if (showStatus) {
          setShowStatus(false);
          setTimeout(() => setShowStatus(true), 0);
        }
      } else {
        alert('Failed to submit one or more annotations.');
      }
    } catch (error) {
      console.error('Error submitting annotations:', error);
    }
  }, [currentComment, currentTask, selectedSubtaskLabels, selectedSubtaskTexts, username, fetchUnannotatedComment, showToxicitySubtasks]);

  // Helper function to submit annotations
  const submitAnnotation = async (annotationData) => {
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
      } else {
        console.error('Failed to submit annotation');
      }
      return response;
    } catch (error) {
      console.error('Error submitting annotation:', error);
      return { ok: false };
    }
  };

  const TaskSelection = ({ currentTask, onTaskSelect }) => {
    return (
      <div className="task-selection">
        {Object.keys(tasks).map((taskKey) => {
          const task = tasks[taskKey];
          const Icon = taskIcons[taskKey]; // Make sure this key exists in taskIcons
          return (
            <button
              key={taskKey}
              onClick={() => onTaskSelect(taskKey)}
              className={currentTask === taskKey ? 'task-button selected' : 'task-button'}
            >
              {Icon && <Icon />} {task.name}
            </button>
          );
        })}
      </div>
    );
  };


  const LabelSelection = ({ taskKey, onLabelSelect, selectedSubtaskTexts }) => {

    const task = tasks[taskKey];
    if (!task) {
      return null;
    }
  
    // Ensure selectedSubtaskTexts is defined before passing it to the render function
    selectedSubtaskTexts = selectedSubtaskTexts || {};
  
    // Call the render function of the current task
    return task.render(selectedSubtaskLabels, onLabelSelect, selectedSubtaskTexts);
  };
  
  const TextInputSubtask = React.memo(({ subtask, onTextChange, textValue }) => {
    const inputRef = useRef(null);
  
    // Focus the input when the component mounts or when the value changes
    useEffect(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, [textValue]);
  
    return (
      <>
        <h3>{subtask.name}</h3>
        <div className="text-input-subtask">
          <input
            ref={inputRef} // Set the ref to the input element
            type="text"
            value={textValue}
            onChange={(e) => onTextChange(subtask.key, e.target.value)}
          />
        </div>
      </>
    );
  });

  const handleLabelSelect = (label, subtaskName) => {
    setSelectedSubtaskLabels(prevSubtaskLabels => {
      const updatedSubtaskLabels = { ...prevSubtaskLabels };
      const binarySubtasks = [
        'toxicityLevel', 'typeOfToxicity', 'hateSpeechDetection', 'target', 
        'aggressiveness', 'encouragement', 'sympathy', 'consent', 'overallConstructiveness'
      ];
  
      if (binarySubtasks.includes(subtaskName)) {
        // For binary subtasks, enforce that selecting one option deselects the other
        updatedSubtaskLabels[subtaskName] = [label];
      } else {
        // For non-binary subtasks, toggle the selection
        const currentLabels = updatedSubtaskLabels[subtaskName] || [];
        if (currentLabels.includes(label)) {
          updatedSubtaskLabels[subtaskName] = currentLabels.filter(l => l !== label);
        } else {
          updatedSubtaskLabels[subtaskName] = [...currentLabels, label];
        }
      }
  
      // Logic to determine visibility of subtasks based on selected labels
      if (subtaskName === 'toxicityLevel') {
        const showTypeOfToxicity = label === 'Særandi';
        setShowToxicitySubtasks({ typeOfToxicity: showTypeOfToxicity, targetOfToxicity: false });
      }
      if (subtaskName === 'typeOfToxicity') {
        const showTargetOfToxicity = label === 'Markviss móðgun';
        setShowToxicitySubtasks(prev => ({ ...prev, targetOfToxicity: showTargetOfToxicity }));
      }
      if (subtaskName === 'hateSpeechDetection') {
        setShowHateSpeechSubtasks(label === 'Hatursorðræða');
      }
  
      return updatedSubtaskLabels;
    });
  };

  const handleTextChange = useCallback((subtaskName, textValue) => {
    setSelectedSubtaskTexts(prevSubtaskTexts => ({
      ...prevSubtaskTexts,
      [subtaskName]: textValue
    }));
  }, []);
  

  const tasks = {
    sentiment: {
      name: 'Einföld lyndisgreining',
      subtasks: {
        sentiment: {
          name: 'Lyndi',
          labels: ['Jákvætt', 'Neikvætt', 'Hlutlaust']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        // Retrieve the selected labels for the 'Einföld lyndisgreining' subtask
        return (
          <>
            <h2>Einföld lyndisgreining</h2>
            {Object.entries(tasks.sentiment.subtasks).map(([subtaskKey, subtask]) => (
              <div key={subtaskKey}>
                <h3>{subtask.name}</h3>
                <div className="label-selection">
                  {subtask.labels.map(label => (
                    <button
                      key={label}
                      onClick={() => handleLabelSelect(label, subtaskKey)}
                      className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </>
        );
      },
    },
    /*deepSentiment: {
      name: 'Dýpri lyndisgreining',
      subtasks: {
        emotionalState: {
          labels: ['Jákvætt', 'Neikvætt', 'Blendnar tilfinningar', 'Óþekkt'],
          name: 'Tilfinningalegt ástand'
        },
        mainSubject: {
          name: 'Aðalviðfangsefni'
        },
        attitudeTowardsSubject: {
          labels: ['Jákvætt', 'Neikvætt', 'Blandað viðhorf', 'Óþekkt'],
          name: 'Viðhorf til aðalviðfangsefnis'
        },
        generalAttitude: {
          labels: ['Jákvætt', 'Neikvætt', 'Blandað (jákvætt og neikvætt)', 'Blandað (andstæðar fylkingar)', 'Ekkert'],
          name: 'Almennt viðhorf til aðalviðfangsefnisins'
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect, selectedSubtaskTexts) => {
        // Render the subtasks for deepSentiment
        return (
          <>
            <h2>Dýpri lyndisgreining</h2>
            {Object.entries(tasks.deepSentiment.subtasks).map(([subtaskKey, subtask]) => {
              if (subtask.labels) {
                // Render label selection for subtasks with labels
                return (
                  <div key={subtaskKey}>
                    <h3>{subtask.name}</h3>
                    <div className="label-selection">
                      {subtask.labels.map(label => (
                        <button
                          key={label}
                          onClick={() => handleLabelSelect(label, subtaskKey)}
                          className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              } else {
                // Render text input for subtasks without labels
                return (
                  <TextInputSubtask
                    key={subtaskKey}
                    subtask={{ ...subtask, key: subtaskKey }} // Pass the subtaskKey as part of the subtask object
                    onTextChange={handleTextChange} // Pass handleTextChange here
                    textValue={selectedSubtaskTexts[subtaskKey] || ''}
                  />
                );
              }
            })}
          </>
        );
      },
    },*/
    toxicity: {
      name: 'Greining á særandi orðbragði',
      subtasks: {
        toxicityLevel: {
          name: 'Særandi eða ekki',
          labels: ['Særandi', 'Ekki særandi']
        },
        typeOfToxicity: {
          name: 'Flokkun meiðyrða',
          labels: ['Markviss móðgun', 'Ómarkvisst']
        },
        targetOfToxicity: {
          name: 'Staðfesting á marki meiðyrða',
          labels: ['Einstaklingur', 'Hópur', 'Annað']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        return (
          <>
            <h2>{tasks.toxicity.name}</h2>
            {Object.entries(tasks.toxicity.subtasks).map(([subtaskKey, subtask]) => {
              // Only render subtasks based on the visibility state
              if (subtaskKey === 'typeOfToxicity' && !showToxicitySubtasks.typeOfToxicity) {
                return null;
              }
              if (subtaskKey === 'targetOfToxicity' && !showToxicitySubtasks.targetOfToxicity) {
                return null;
              }
              return (
                <div key={subtaskKey}>
                  <h3>{subtask.name}</h3>
                  <div className="label-selection">
                    {subtask.labels.map(label => (
                      <button
                        key={label}
                        onClick={() => handleLabelSelect(label, subtaskKey)}
                        className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </>
        );
      },
    },
    hateSpeech: {
      name: 'Hatursorðræðugreining',
      subtasks: {
        hateSpeechDetection: {
          name: 'Hatursorðræða eða ekki',
          labels: ['Ekki hatursorðræða', 'Hatursorðræða']
        },
        premises: {
          name: 'Forsendur',
          labels: ['Innflytjendur', 'Trúarbrögð', 'Fötlun', 'Konur', 'Hinsegin']
        },
        target: {
          name: 'Marksvið',
          labels: ['Hópur', 'Einstaklingur']
        },
        aggressiveness: {
          name: 'Ágengni',
          labels: ['Ágengni', 'Ekki ágengni']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        return (
          <>
            <h2>{tasks.hateSpeech.name}</h2>
            {Object.entries(tasks.hateSpeech.subtasks).map(([subtaskKey, subtask]) => {
              // Skip rendering other subtasks if hate speech is detected
              if (subtaskKey !== 'hateSpeechDetection' && !showHateSpeechSubtasks) {
                return null;
              }
              return (
                <div key={subtaskKey}>
                  <h3>{subtask.name}</h3>
                  <div className="label-selection">
                    {subtask.labels.map(label => (
                      <button
                        key={label}
                        onClick={() => handleLabelSelect(label, subtaskKey)}
                        className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </>
        );
      },
    },
    emotionDetection: {
      name: 'Tilfinningagreining',
      subtasks: {
        emotion: {
          name: 'Tilfinning',
          labels: ['Fyrirlitning', 'Gleði', 'Hræðsla', 'Reiði', 'Sorg', 'Undrun', 'Hneykslun', 'Ógeðistilfinning', 'Hlutlaust']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        // Retrieve the selected labels for the 'Tilfinningagreining' subtask
        return (
          <>
            <h2 style={{ textAlign: 'left', width: '100%' }}>Tilfinningagreining</h2>
            {Object.entries(tasks.emotionDetection.subtasks).map(([subtaskKey, subtask]) => (
              <div key={subtaskKey}>
                <h3>{subtask.name}</h3>
                <div className="label-selection">
                  {subtask.labels.map(label => (
                    <button
                      key={label}
                      onClick={() => handleLabelSelect(label, subtaskKey)}
                      className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </>
        );
      },
    },
    encouragementAndSympathy: {
      name: 'Hvatninga- og Samúðargreining',
      subtasks: {
        encouragement: {
          name: 'Hvatning',
          labels: ['Hvatning', 'Engin hvatning']
        },
        sympathy: {
          name: 'Samúð',
          labels: ['Samúð', 'Engin samúð']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        return (
          <>
            <h2 style={{ textAlign: 'left', width: '100%' }}>Hvatninga- og Samúðargreining</h2>
            {Object.entries(tasks.encouragementAndSympathy.subtasks).map(([subtaskKey, subtask]) => (
              <div key={subtaskKey}>
                <h3 style={{ textAlign: 'left', width: '100%' }}>{subtask.name}</h3>
                <div className="label-selection" style={{ textAlign: 'left', width: '100%' }}>
                  {subtask.labels.map(label => (
                    <button
                      key={label}
                      onClick={() => handleLabelSelect(label, subtaskKey)}
                      className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </>
        );
      },
    },
    constructiveFeedback: {
      name: 'Greining á Uppbyggilegri Endurgjöf',
      subtasks: {
        consent: {
          name: 'Samþykki',
          labels: ['Já', 'Nei']
        },
        constructiveTraits: {
          name: 'Uppbyggilegir eiginleikar',
          labels: ['Koma með lausn', 'Ræða ákveðna punkta', 'Koma fram með sannanir', 'Ræða persónulega reynslu', 'Leggja eitthvað markvert til samtalsins og hvetja til skoðanaskipta', 'Ummælin hafa ekki uppbyggileg einkenni']
        },
        nonConstructiveTraits: {
          name: 'Óuppbyggilegir eiginleikar',
          labels: ['Eru óviðkomandi umræðunni', 'Bera ekki virðingu fyrir skoðun eða trú annarra', 'Eru veigalítil', 'Eru kaldhæðin', 'Eru ögrandi', 'Ummælin hafa ekki óuppbyggileg einkenni']
        },
        overallConstructiveness: {
          name: 'Uppbyggilegt',
          labels: ['Já', 'Nei']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        return (
          <>
            <h2 style={{ textAlign: 'left', width: '100%' }}>Greining á Uppbyggilegri Endurgjöf</h2>
            {Object.entries(tasks.constructiveFeedback.subtasks).map(([subtaskKey, subtask]) => (
              <div key={subtaskKey}>
                <h3 style={{ textAlign: 'left', width: '100%' }}>{subtask.name}</h3>
                <div className="label-selection">
                  {subtask.labels.map(label => (
                    <button
                      key={label}
                      onClick={() => handleLabelSelect(label, subtaskKey)}
                      className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </>
        );
      },
    },
    sarcasmDetection: {
      name: 'Kaldhæðnigreining',
      subtasks: {
        sarcasm: {
          name: 'Kaldhæðnigreining - Kaldhæðni eða ekki',
          labels: ['Kaldhæðin', 'Ekki kaldhæðin', 'Óljós']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        // Retrieve the selected labels for the 'Einföld lyndisgreining' subtask
        return (
          <>
            <h2>Kaldhæðnigreining</h2>
            {Object.entries(tasks.sarcasmDetection.subtasks).map(([subtaskKey, subtask]) => (
              <div key={subtaskKey}>
                <h3>{subtask.name}</h3>
                <div className="label-selection">
                  {subtask.labels.map(label => (
                    <button
                      key={label}
                      onClick={() => handleLabelSelect(label, subtaskKey)}
                      className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </>
        );
      },
    },
    trollDetection: {
      name: 'Tröllaveiði',
      subtasks: {
        trollOrNot: {
          name: 'Tröllaveiði - Nettröll eða ekki',
          labels: ['Nettröll', 'Ekki nettröll', 'Óljóst']
        }
      },
      render: (selectedSubtaskLabels, handleLabelSelect) => {
        // Retrieve the selected labels for the 'Einföld lyndisgreining' subtask
        return (
          <>
            <h2>Tröllaveiði</h2>
            {Object.entries(tasks.trollDetection.subtasks).map(([subtaskKey, subtask]) => (
              <div key={subtaskKey}>
                <h3>{subtask.name}</h3>
                <div className="label-selection">
                  {subtask.labels.map(label => (
                    <button
                      key={label}
                      onClick={() => handleLabelSelect(label, subtaskKey)}
                      className={selectedSubtaskLabels[subtaskKey]?.includes(label) ? 'selected' : ''}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </>
        );
      },
    },
  };
  

  return (
    <div className="App">
      <div className={`auth-top-bar ${isDrawerOpen ? 'expanded' : ''}`}>
        <button className={`hamburger ${loggedIn ? 'logged-in' : ''}`} onClick={toggleDrawer}>
          {isDrawerOpen ? 'Fela verkefnaval' : 'Sýna verkefnaval'}
        </button>
        <div className="auth-controls">
        {!loggedIn && (
            <>
            <Login
              username={username}
              password={password}
              onLogin={login}
              onRegister={register}
              setUsername={setUsername}
              setPassword={setPassword}
              error={error}
              setError={setError}
            />  
              {/* Remove any Register component rendering or logic related to toggling showRegister */}
            </>
          )}
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
              {showBlogPost ? 'Hide blog' : 'Sýna bloggfærslu'}
            </button>
            {showBlogPost && (
              <>
                <h3><a href={currentComment.blogPost.link} target="_blank" rel="noopener noreferrer">{currentComment.blogPost.title}</a></h3>
                <p dangerouslySetInnerHTML={{ __html: currentComment.blogPost.text }}></p>
              </>
            )}
          </div>
        )}
        {currentComment && currentComment.precedingComments && currentComment.precedingComments.length > 0 && (
          <div className="preceding-comments">
            <button className="toggle-button" onClick={() => setShowPrecedingComments(!showPrecedingComments)}>
              {showPrecedingComments ? 'Hide prior comments' : 'Sýna fyrri athugasemdir'}
            </button>
            {showPrecedingComments && currentComment.precedingComments.map((c) => (
              <div key={c.id} className="preceding-comment">
                <p dangerouslySetInnerHTML={{ __html: c.text }}></p>
                <span className="comment-signature" dangerouslySetInnerHTML={{ __html: c.signature }}></span>
              </div>
            ))}
          </div>
        )}
        <div className="current-comment">
          <p dangerouslySetInnerHTML={{ __html: currentComment.text }}></p>
          <span className="comment-signature" dangerouslySetInnerHTML={{ __html: currentComment.signature }}></span>
        </div>
        {currentTask && (
          <div className="label-selection-container">
            <LabelSelection
              taskKey={currentTask}
              onLabelSelect={handleLabelSelect}
              selectedSubtaskTexts={selectedSubtaskTexts} // Pass the selectedSubtaskTexts to LabelSelection
            />
          </div>
        )}
        {currentTask && (<div className="submit-button-container">
          <button onClick={handleSubmit} className="submit-button">
            Skrá mörkun
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
        <button onClick={toggleStatus} className="instructions-toggle-button">
          {showStatus ? 'Fela stöðu' : 'Sýna stöðu'}
        </button>
        {showInstructions && (
          <div className="instructions-container">
            <h2>Leiðbeiningar</h2>
            {currentTask && <TaskInstructions taskName={currentTask} />}
          </div>
        )}
        {showStatus && (
          <UserStatus/>
        )}
      </div>
    )}
    </div>
  );
};

export default App;

