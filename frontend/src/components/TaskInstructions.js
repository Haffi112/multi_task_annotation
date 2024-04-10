import React, { useState, useEffect } from 'react';
import { marked } from 'marked';

const TaskInstructions = ({ taskName }) => {
  const [instructions, setInstructions] = useState('');

  useEffect(() => {
    fetch(`/instructions/${taskName}.md`)
      .then(response => response.text())
      .then(text => setInstructions(marked(text)))
      .catch(console.error);
  }, [taskName]);

  return (
    <div className="task-instructions" dangerouslySetInnerHTML={{ __html: instructions }} />
  );
};

export default TaskInstructions;