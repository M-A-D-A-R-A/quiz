import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
const BASE_URL = "https://quiz-production-e8f0.up.railway.app/headout/api";
// // Sample data
// const destinations = [
//   {
//     city: "Paris",
//     country: "France",
//     clues: [
//       "This city is home to a famous tower that sparkles every night.",
//       "Known as the 'City of Love' and a hub for fashion and art."
//     ],
//     fun_fact: [
//       "The Eiffel Tower was supposed to be dismantled after 20 years but was saved because it was useful for radio transmissions!",
//       "Paris has only one stop sign in the entire city—most intersections rely on priority-to-the-right rules."
//     ],
//     trivia: [
//       "This city is famous for its croissants and macarons. Bon appétit!",
//       "Paris was originally a Roman city called Lutetia."
//     ]
//   },
//   {
//     city: "Tokyo",
//     country: "Japan",
//     clues: [
//       "This city has the world's busiest pedestrian crossing.",
//       "Home to over 14,000 vending machines selling everything from drinks to umbrellas."
//     ],
//     fun_fact: [
//       "Tokyo has more Michelin-starred restaurants than any other city in the world!",
//       "The Imperial Palace grounds in the center of Tokyo are said to be worth more than all the real estate in California."
//     ],
//     trivia: [
//       "Tokyo was formerly known as Edo until 1868.",
//       "The Tokyo Skytree is the tallest tower in the world at 634 meters."
//     ]
//   },
//   {
//     city: "New York",
//     country: "USA",
//     clues: [
//       "This city has a famous statue that was gifted by France.",
//       "Known as the 'Big Apple' and never seems to sleep."
//     ],
//     fun_fact: [
//       "There's a hidden train track beneath the Waldorf Astoria hotel used by presidents and VIPs!",
//       "New York's subway system has 472 stations—the most of any transit system in the world."
//     ],
//     trivia: [
//       "New York was briefly the capital of the United States from 1785 to 1790.",
//       "Over 800 languages are spoken in this diverse city, making it the most linguistically diverse city in the world."
//     ]
//   },
//   {
//     city: "Sydney",
//     country: "Australia",
//     clues: [
//       "This city is famous for its opera house with sail-like roofs.",
//       "Home to one of the largest natural harbors in the world."
//     ],
//     fun_fact: [
//       "The Sydney Harbour Bridge is nicknamed 'The Coathanger' because of its arch-based design!",
//       "Sydney's Opera House has over one million roof tiles, despite appearing smooth from a distance."
//     ],
//     trivia: [
//       "Sydney was founded in 1788 as a penal colony for British convicts.",
//       "The Sydney Opera House took 14 years to build, ten years longer than planned."
//     ]
//   },
//   {
//     city: "Rome",
//     country: "Italy",
//     clues: [
//       "This city has a famous ancient amphitheater where gladiators once fought.",
//       "Known as the 'Eternal City' with a history spanning over 28 centuries."
//     ],
//     fun_fact: [
//       "There's a secret keyhole in Rome that perfectly frames St. Peter's Basilica!",
//       "Romans throw about €1.5 million in coins into the Trevi Fountain each year, all donated to charity."
//     ],
//     trivia: [
//       "Rome has more fountains than any other city in the world—over 2,000!",
//       "The Romans built such good roads that many are still in use today, 2,000 years later."
//     ]
//   }
// ];

// Create a component for the confetti animation
const Confetti = () => {
  const [confetti, setConfetti] = useState([]);
  
  useEffect(() => {
    const colors = ['#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4', '#00bcd4'];
    const newConfetti = [];
    
    for (let i = 0; i < 100; i++) {
      newConfetti.push({
        id: i,
        x: Math.random() * 100,
        y: -20 - Math.random() * 80,
        size: 5 + Math.random() * 10,
        color: colors[Math.floor(Math.random() * colors.length)],
        speed: 2 + Math.random() * 5
      });
    }
    
    setConfetti(newConfetti);
    
    const interval = setInterval(() => {
      setConfetti(prev => 
        prev.map(c => ({
          ...c,
          y: c.y + c.speed,
          x: c.x + (Math.random() - 0.5) * 2
        }))
      );
    }, 50);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      overflow: 'hidden',
      pointerEvents: 'none'
    }}>
      {confetti.map(c => (
        <div 
          key={c.id}
          style={{
            position: 'absolute',
            left: `${c.x}%`,
            top: `${c.y}%`,
            width: `${c.size}px`,
            height: `${c.size}px`,
            backgroundColor: c.color,
            borderRadius: '50%'
          }}
        />
      ))}
    </div>
  );
};

const TravelQuizGame = () => {
  const [score, setScore] = useState({ correct: 0, incorrect: 0 });
  const [currentDestination, setCurrentDestination] = useState(null);
  const [selectedClues, setSelectedClues] = useState([]);
  const [options, setOptions] = useState([]);
  const [userAnswer, setUserAnswer] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [funFact, setFunFact] = useState("");
  const [questionData, setQuestionData] = useState(null);
  //   const [userAnswer, setUserAnswer] = useState(null);
  

  
const fetchQuestion = () => {
  fetch(`${BASE_URL}/questions`, {
    method: "GET",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      setQuestionData(data);
      setUserAnswer(null);
      setShowConfetti(false);
      setFunFact("");

      // Select 1-2 random clues
      const numClues = Math.floor(Math.random() * 2) + 1; // 1 or 2 clues
      const shuffledClues = [...data.clues].sort(() => Math.random() - 0.5);
      setSelectedClues(shuffledClues.slice(0, numClues));

      // Shuffle options
      const shuffledOptions = [...data.choices].sort(() => Math.random() - 0.5);
      setOptions(shuffledOptions);
      console.log(data)
      console.log(shuffledOptions)
    })
    .catch((error) => console.error("Error fetching question:", error));
};

useEffect(() => {
  fetchQuestion();
}, []);
  
  // Handle user answer
  const handleAnswer = (answer) => {
    if (!questionData) return;

    const url = `${BASE_URL}/answer?question_id=${questionData.question_id}&answer_id=${answer.id}`;

    fetch(url, {
      method: "POST",
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((data) => {
        const isCorrect = data.correct;

        setUserAnswer({ selected: answer, isCorrect });
        setFunFact(isCorrect ? `🎉 Correct! ${data.fun_fact}` : `❌ Oops! The correct answer was ${data.city}.`);

        if (isCorrect) {
          setShowConfetti(true);
          setScore((prev) => ({ ...prev, correct: prev.correct + 1 }));
        } else {
          setScore((prev) => ({ ...prev, incorrect: prev.incorrect + 1 }));
        }
      })
      .catch((error) => console.error("Error validating answer:", error));
  };

  
  const containerStyle = {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '24px',
    background: 'linear-gradient(to bottom right, #f0f4ff, #f5f0ff)',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    position: 'relative',
    minHeight: '100vh'
  };
  
  const headerStyle = {
    textAlign: 'center',
    marginBottom: '32px'
  };
  
  const titleStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#4338ca',
    marginBottom: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };
  
  const scoreContainerStyle = {
    background: 'white',
    padding: '12px',
    borderRadius: '9999px',
    display: 'inline-flex',
    gap: '16px',
    boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)'
  };
  
  const cardStyle = {
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    marginBottom: '24px'
  };
  
  const clueStyle = {
    padding: '12px',
    background: '#eef3ff',
    borderRadius: '8px',
    color: '#4b5563',
    marginBottom: '12px'
  };
  
  const optionsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '16px',
    marginBottom: '24px'
  };
  
  const buttonStyle = {
    background: '#4f46e5',
    color: 'white',
    padding: '12px 16px',
    borderRadius: '8px',
    border: 'none',
    fontWeight: '500',
    fontSize: '18px',
    cursor: 'pointer',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    transition: 'background-color 0.2s'
  };
  
  const buttonHoverStyle = {
    background: '#4338ca'
  };
  
  const resultCardStyle = (isCorrect) => ({
    background: isCorrect ? '#ecfdf5' : '#fef2f2',
    borderLeft: `4px solid ${isCorrect ? '#10b981' : '#ef4444'}`,
    padding: '16px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'flex-start'
  });
  
  const nextButtonStyle = {
    width: '100%',
    background: '#7c3aed',
    color: 'white',
    padding: '12px 16px',
    borderRadius: '8px',
    border: 'none',
    fontWeight: '500',
    fontSize: '18px',
    cursor: 'pointer',
    marginTop: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };
  
  return (
    <div style={containerStyle}>
      {showConfetti && <Confetti />}
      
      <div style={headerStyle}>
        <h1 style={titleStyle}>
          <span style={{ marginRight: '8px' }}>✨</span>
          Travel Quiz
          <span style={{ marginLeft: '8px' }}>✨</span>
        </h1>
        <div style={scoreContainerStyle}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ fontWeight: 'bold', color: '#16a34a', fontSize: '18px' }}>{score.correct}</span>
            <span style={{ marginLeft: '4px', color: '#6b7280' }}>correct</span>
          </div>
          <div style={{ height: '32px', width: '1px', background: '#e5e7eb' }}></div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ fontWeight: 'bold', color: '#dc2626', fontSize: '18px' }}>{score.incorrect}</span>
            <span style={{ marginLeft: '4px', color: '#6b7280' }}>incorrect</span>
          </div>
        </div>
      </div>
      
      <div style={cardStyle}>
        <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', marginBottom: '16px' }}>Where am I?</h2>
        <div>
          {selectedClues.map((clue, idx) => (
            <div key={idx} style={clueStyle}>
              {clue}
            </div>
          ))}
        </div>
      </div>
      
      {!userAnswer ? (
        <div style={optionsGridStyle}>
          {options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleAnswer(option)}
              style={buttonStyle}
              onMouseOver={(e) => {
                e.currentTarget.style.background = buttonHoverStyle.background;
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = buttonStyle.background;
              }}
            >
              {option.name}
            </button>
          ))}
        </div>
      ) : (
        <div style={{ marginBottom: '24px' }}>
          {userAnswer.isCorrect ? (
    <div style={resultCardStyle(true)}>
      <div style={{ fontSize: "32px", marginRight: "12px" }}>🎉</div>
      <div>
        <h3 style={{ fontWeight: "bold", color: "#065f46" }}>Correct!</h3>
        <p style={{ color: "#047857" }}>{userAnswer.selected.name}</p>
        <p style={{ marginTop: "8px", color: "#4b5563" }}>{funFact}</p>
      </div>
    </div>
  ) : (
    <div style={resultCardStyle(false)}>
      <div style={{ fontSize: "32px", marginRight: "12px" }}>😢</div>
      <div>
        <h3 style={{ fontWeight: "bold", color: "#991b1b" }}>Not quite!</h3>
        <p style={{ color: "#b91c1c" }}>
          You selected: {userAnswer.selected.name} <br />
          Correct answer: {userAnswer.correctCity}
        </p>
        <p style={{ marginTop: "8px", color: "#4b5563" }}>{funFact}</p>
      </div>
    </div>
  )}
          
          <button
            onClick={fetchQuestion}
            style={nextButtonStyle}
          >
            Next Destination
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor" style={{ marginLeft: '8px' }}>
              <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

export default TravelQuizGame;

// import { useState, useEffect } from "react";



// const TravelQuizGame = () => {
//   const [score, setScore] = useState({ correct: 0, incorrect: 0 });
//   const [questionData, setQuestionData] = useState(null);
//   const [selectedClues, setSelectedClues] = useState([]);
//   const [options, setOptions] = useState([]);
//   const [userAnswer, setUserAnswer] = useState(null);
//   const [showConfetti, setShowConfetti] = useState(false);
//   const [funFact, setFunFact] = useState("");

//   // Fetch a new question from the API
//   const fetchQuestion = () => {
//     fetch(`${BASE_URL}/questions`, {
//       method: "GET",
//       mode: "cors",
//       headers: {
//         "Content-Type": "application/json",
//       },
//     })
//       .then((res) => res.json())
//       .then((data) => {
//         setQuestionData(data);
//         setUserAnswer(null);
//         setShowConfetti(false);
//         setFunFact("");

//         // Select 1-2 random clues
//         const numClues = Math.floor(Math.random() * 2) + 1; // 1 or 2 clues
//         const shuffledClues = [...data.clues].sort(() => Math.random() - 0.5);
//         setSelectedClues(shuffledClues.slice(0, numClues));

//         // Shuffle options
//         const shuffledOptions = [...data.choices].sort(() => Math.random() - 0.5);
//         setOptions(shuffledOptions);
//       })
//       .catch((error) => console.error("Error fetching question:", error));
//   };

//   useEffect(() => {
//     fetchQuestion();
//   }, []);

//   // Handle user answer
//   const handleAnswer = (answer) => {
//     if (!questionData) return;

//     const url = `${BASE_URL}/answer?question_id=${questionData.question_id}&answer_id=${answer.id}`;

//     fetch(url, {
//       method: "POST",
//       mode: "cors",
//       headers: {
//         "Content-Type": "application/json",
//       },
//     })
//       .then((res) => res.json())
//       .then((data) => {
//         const isCorrect = data.correct;

//         setUserAnswer({ selected: answer, isCorrect });
//         setFunFact(isCorrect ? `🎉 Correct! ${data.fun_fact}` : `❌ Oops! The correct answer was ${data.city}.`);

//         if (isCorrect) {
//           setShowConfetti(true);
//           setScore((prev) => ({ ...prev, correct: prev.correct + 1 }));
//         } else {
//           setScore((prev) => ({ ...prev, incorrect: prev.incorrect + 1 }));
//         }
//       })
//       .catch((error) => console.error("Error validating answer:", error));
//   };

//   if (!questionData) {
//     return <div style={{ padding: "32px", textAlign: "center" }}>Loading...</div>;
//   }

//   return (
//     <div style={{ padding: "20px", maxWidth: "500px", margin: "auto", textAlign: "center" }}>
//       <h2>Guess the City</h2>
//       <div>
//         {selectedClues.map((clue, index) => (
//           <p key={index}>🔹 {clue}</p>
//         ))}
//       </div>

//       <h3>Choices:</h3>
//       <ul style={{ listStyleType: "none", padding: 0 }}>
//         {options.map((choice) => (
//           <li
//             key={choice.id}
//             onClick={() => handleAnswer(choice)}
//             style={{
//               cursor: "pointer",
//               background: userAnswer?.selected?.id === choice.id ? (userAnswer.isCorrect ? "#4caf50" : "#ff4c4c") : "#f0f0f0",
//               padding: "10px",
//               margin: "5px 0",
//               borderRadius: "5px",
//               transition: "0.3s",
//             }}
//           >
//             {choice.name}
//           </li>
//         ))}
//       </ul>

//       {userAnswer && <p style={{ marginTop: "10px", fontWeight: "bold" }}>{funFact}</p>}

//       <button
//         onClick={fetchQuestion}
//         style={{
//           marginTop: "20px",
//           padding: "10px 15px",
//           background: "#007bff",
//           color: "#fff",
//           border: "none",
//           borderRadius: "5px",
//           cursor: "pointer",
//         }}
//       >
//         Next Question
//       </button>

//       <h4>Score: ✅ {score.correct} | ❌ {score.incorrect}</h4>
//     </div>
//   );
// };

// export default TravelQuizGame;
