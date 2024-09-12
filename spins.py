import cupy as cp
from joblib import Parallel, delayed

# Параметры
params = {
    "base_rewards": [0, 2, 5, 10, 20, 30, 50, 100],
    "zero_reward_percentage": 0.30,  # Фиксированное значение для нулевого выигрыша
    "target_amount": 1500,
    "days_until_purchase": 3,
    "referral_bonus": 300,
    "referral_probability": 0.05,
    "task_claim": 50,
    "spins_per_day": 80,
    "confidence_interval": 0.05
}

log_entries = []  # Для записи логов

# Функция для записи логов по мере их появления
def write_logs():
    with open("spinlog.txt", "a") as log_file:  # Используем 'a' для добавления логов без перезаписи файла
        log_file.write(log_entries[-1])  # Пишем только последний элемент

# Линейное распределение вероятностей внутри сегмента
def linear_prob_distribution(rewards, prob_sum):
    num_rewards = len(rewards)
    if num_rewards == 0:
        return cp.array([], dtype=cp.float32)

    probabilities = cp.linspace(1, 0.1, num_rewards, dtype=cp.float32)
    probabilities = probabilities / cp.sum(probabilities) * prob_sum
    return probabilities

# Полное распределение вероятностей с учетом условий
def full_probability_distribution(base_rewards, zero_reward_percentage, small_coef, medium_coef, alpha):
    remaining_probability = 1 - zero_reward_percentage
    probabilities = [zero_reward_percentage]

    # Мелкие выигрыши (2, 5, 10)
    small_rewards = [r for r in base_rewards if r <= 10]
    small_prob_sum = small_coef * remaining_probability

    # Средние выигрыши (20, 30)
    medium_rewards = [r for r in base_rewards if 20 <= r <= 30]
    medium_prob_sum = medium_coef * remaining_probability

    # Крупные выигрыши (50, 100)
    large_rewards = [r for r in base_rewards if r > 30]
    large_prob_sum = (1 - small_coef - medium_coef) * remaining_probability

    small_prob = linear_prob_distribution(small_rewards, small_prob_sum)
    medium_prob = linear_prob_distribution(medium_rewards, medium_prob_sum)

    exp_prob = cp.exp(-alpha * cp.array(large_rewards))
    exp_prob = exp_prob / exp_prob.sum() * large_prob_sum

    for reward in base_rewards[1:]:
        if reward in small_rewards:
            probabilities.append(small_prob[small_rewards.index(reward)] if small_prob.size > 0 else 0.01)
        elif reward in medium_rewards:
            probabilities.append(medium_prob[medium_rewards.index(reward)] if medium_prob.size > 0 else 0.01)
        elif reward in large_rewards:
            probabilities.append(exp_prob[large_rewards.index(reward)] if exp_prob.size > 0 else 0.01)

    probabilities = cp.array(probabilities)
    probabilities[probabilities <= 0] = 0.01
    remaining_sum = 1 - probabilities[0]
    probabilities[1:] = probabilities[1:] / cp.sum(probabilities[1:]) * remaining_sum

    return probabilities

# Монтекарло симуляция для проверки результата
def monte_carlo_simulation(base_rewards, probabilities, spins_per_day, days, referral_bonus, referral_probability, task_claim, simulations=100):
    results = []
    total_spins = spins_per_day * days

    for _ in range(simulations):
        total_coins = 0
        for _ in range(total_spins):
            spin_result = cp.random.choice(base_rewards, p=probabilities)
            total_coins += spin_result

        total_coins += days * task_claim
        total_coins += days * referral_bonus * referral_probability

        results.append(total_coins)

    return cp.array(results, dtype=cp.float32)

# Запуск симуляции для комбинации
def run_simulation(combo, params):
    small_coef, medium_coef, alpha = combo
    log_message = f"Запуск симуляции для комбинации: Мелкие: {small_coef:.2f}, Средние: {medium_coef:.2f}, Alpha: {alpha:.2f}\n"
    print(log_message)
    log_entries.append(log_message)
    write_logs()  # Добавляем запись логов

    probabiliti_reward = full_probability_distribution(
        params["base_rewards"], params["zero_reward_percentage"], small_coef, medium_coef, alpha
    )

    simulated_results = monte_carlo_simulation(
        params["base_rewards"], probabiliti_reward, params["spins_per_day"],
        params["days_until_purchase"], params["referral_bonus"],
        params["referral_probability"], params["task_claim"], simulations=300  # Увеличиваем количество симуляций для большей точности
    )

    mean_result = cp.mean(simulated_results)
    result_message = f"Средний результат для комбинации {small_coef:.2f}, {medium_coef:.2f}, Alpha: {alpha:.2f}: {mean_result:.2f}\n"
    print(result_message)
    log_entries.append(result_message)
    write_logs()  # Добавляем запись логов

    # Выводим вероятности для каждого значения наград
    prob_message = f"Вероятности для наград: {probabiliti_reward}\n"
    print(prob_message)
    log_entries.append(prob_message)
    write_logs()  # Запись вероятностей в логи

    return small_coef, medium_coef, alpha, mean_result

# Параллельная обработка комбинаций с использованием joblib
def parallel_monte_carlo(combinations, params):
    results = Parallel(n_jobs=-1)(delayed(run_simulation)(combo, params) for combo in combinations)
    return results

# Самооптимизация с более агрессивной корректировкой
def adaptive_search(base_rewards, params, target_amount, confidence_interval, simulations=10, max_iterations=10):
    confidence_interval_min = target_amount * (1 - confidence_interval)
    confidence_interval_max = target_amount * (1 + confidence_interval)

    small_coef_range = [0.01, 0.10]
    medium_coef_range = [0.01, 0.10]
    alpha_range = [0.1, 1.5]
    step = 0.05
    iteration = 0
    previous_best_result = None  # Для отслеживания улучшений

    log_entries.append("Этап 1: Самоадаптация поиска\n")
    write_logs()

    while iteration < max_iterations:
        combinations = [
            (small_coef, medium_coef, alpha)
            for small_coef in cp.arange(small_coef_range[0], small_coef_range[1], step)
            for medium_coef in cp.arange(medium_coef_range[0], medium_coef_range[1], step)
            for alpha in cp.arange(alpha_range[0], alpha_range[1], step)
        ]
        results = parallel_monte_carlo(combinations, params)

        best_result = None
        best_combo = None

        for small_coef, medium_coef, alpha, mean_result in results:
            if confidence_interval_min <= mean_result <= confidence_interval_max:
                if best_result is None or abs(target_amount - mean_result) < abs(target_amount - best_result):
                    best_result = mean_result
                    best_combo = (small_coef, medium_coef, alpha)

        # Если результат значительно превышает целевой интервал, уменьшаем вероятность крупных выигрышей
        if best_result and best_result > 5000:
            small_coef_range = [max(0.01, best_combo[0] - 0.02), min(0.99, best_combo[0] + 0.01)]
            medium_coef_range = [max(0.01, best_combo[1] - 0.02), min(0.99, best_combo[1] + 0.01)]
            alpha_range = [max(0.1, best_combo[2] - 0.2), min(5, best_combo[2] + 0.1)]
            step = max(step * 0.5, 0.01)  # Уменьшаем шаг более агрессивно
            log_entries.append(f"Корректировка вероятностей: Мелкие: {small_coef_range}, Средние: {medium_coef_range}, Alpha: {alpha_range}\n")
            write_logs()
        else:
            # Если результат ниже, но всё ещё не оптимален, расширяем диапазоны
            small_coef_range = [max(0.01, small_coef_range[0] - 0.05), min(0.99, small_coef_range[1] + 0.05)]
            medium_coef_range = [max(0.01, medium_coef_range[0] - 0.05), min(0.99, medium_coef_range[1] + 0.05)]
            alpha_range = [max(0.1, alpha_range[0] - 0.1), min(5, alpha_range[1] + 0.1)]
            step = min(step * 1.5, 0.1)  # Увеличиваем шаг
            log_entries.append(f"Расширение диапазонов: Мелкие: {small_coef_range}, Средние: {medium_coef_range}, Alpha: {alpha_range}\n")
            write_logs()

        if step < 0.01:
            log_entries.append("Остановка: дальнейшие улучшения минимальны\n")
            write_logs()
            break

        iteration += 1

    return best_combo, best_result

# Запуск
if __name__ == '__main__':
    best_combo, final_result = adaptive_search(
        params["base_rewards"], params, params["target_amount"],
        params["confidence_interval"], simulations=10, max_iterations=5  # Ограничение на количество итераций
    )

    if best_combo is not None:
        print(f"Лучшее совпадение: Мелкие: {best_combo[0]:.2f}, Средние: {best_combo[1]:.2f}, Alpha: {best_combo[2]:.2f}")
        print(f"Финальный результат: {final_result}")
