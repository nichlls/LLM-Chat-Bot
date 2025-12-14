import { useState } from 'react';
import { useCarRecommendations } from './hooks/useCarRecommendations';
import { CarCard } from './components/CarCard';
import styles from './styles/App.module.css';

function App() {
  const [userInput, setUserInput] = useState<string>('');
  const { results, isLoading, error, fetchRecommendations } = useCarRecommendations();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    await fetchRecommendations(userInput);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Car Rental Recommendations</h1>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.inputGroup}>
          <label htmlFor="carQuery" className={styles.label}>
            What type of car are you looking to rent?
          </label>
          <input
            id="carQuery"
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="e.g., any vehicle for no more than 60 per day"
            className={styles.input}
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !userInput.trim()}
          className={styles.button}
        >
          {isLoading ? 'Searching...' : 'Get Recommendations'}
        </button>
      </form>

      {error && (
        <div className={styles.error}>
          Error: {error}
        </div>
      )}

      {results.length > 0 && (
        <div className={styles.resultsSection}>
          <h2 className={styles.resultsTitle}>Recommended Vehicles:</h2>
          <div className={styles.resultsGrid}>
            {results.map((car, index) => (
              <CarCard key={`${car.name}-${index}`} car={car} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
