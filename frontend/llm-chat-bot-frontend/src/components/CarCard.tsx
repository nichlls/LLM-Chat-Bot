import type { CarRecommendation } from '../types/api';
import styles from '../styles/CarCard.module.css';

interface CarCardProps {
  car: CarRecommendation;
}

export const CarCard = ({ car }: CarCardProps) => {
  return (
    <div className={styles.card}>
      <h3 className={styles.cardTitle}>{car.name}</h3>
      <div className={styles.cardDetails}>
        <span className={styles.price}>${car.price_per_day}/day</span>
        <span className={styles.seats}>{car.seats} seats</span>
      </div>
      <p className={styles.reasoning}>{car.reasoning}</p>
    </div>
  );
};
