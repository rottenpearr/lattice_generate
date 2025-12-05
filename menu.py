#!/usr/bin/env python3
"""
Меню-интерфейс для генератора кристаллических решеток
"""

from crystal_generator import CrystalLattice, generate_lattice_parallel, save_xyz
import os


# Создаем папки для организации файлов
def ensure_directories():
    """Создает необходимые папки для хранения файлов"""
    os.makedirs('xyz_files', exist_ok=True)
    os.makedirs('scalability_tests', exist_ok=True)


def print_header():
    """Выводит заголовок программы"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 26 + "ГЕНЕРАТОР РЕШЕТОК" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝\n")


def print_menu():
    """Выводит главное меню"""
    print("\n" + "=" * 70)
    print("ГЛАВНОЕ МЕНЮ")
    print("=" * 70)
    print("1. Генерация решетки (одиночный файл)")
    print("2. Генерировать датасет (множество решеток)")
    print("3. Тест масштабируемости (с графиком)")
    print("4. Информация о решетках")
    print("0. Выход")
    print("=" * 70)


def single_generation():
    """Универсальная генерация одного файла"""
    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ КРИСТАЛЛИЧЕСКОЙ РЕШЕТКИ")
    print("=" * 70)

    # Выбор типа решетки
    print("\nДоступные типы решеток:")
    lattice_list = list(CrystalLattice.LATTICE_TYPES.items())

    # Группируем по сингониям
    by_syngony = {}
    for key, info in lattice_list:
        syngony = info['syngony']
        if syngony not in by_syngony:
            by_syngony[syngony] = []
        by_syngony[syngony].append((key, info))

    idx = 1
    choice_map = {}

    for syngony in ['cubic', 'tetragonal', 'orthorhombic', 'hexagonal',
                    'trigonal', 'monoclinic', 'triclinic']:
        if syngony in by_syngony:
            print(f"\n{syngony.upper()}:")
            for key, info in by_syngony[syngony]:
                print(f"  {idx}. {info['name']}")
                choice_map[idx] = key
                idx += 1

    choice = int(input(f"\nВыберите тип решетки (1-{len(choice_map)}): "))
    lattice_type = choice_map[choice]
    info = CrystalLattice.LATTICE_TYPES[lattice_type]

    print(f"\nВыбрано: {info['name']}")
    print(f"Сингония: {info['syngony']}")
    print(f"Тип центрирования: {info['centering']}")
    print()

    # Параметры решетки
    use_default = input("Использовать параметры по умолчанию (a=b=c=5.0 Å)? (y/n), по умолчанию y: ").lower()

    if use_default != 'n':
        a, b, c = 5.0, 5.0, 5.0
        alpha, beta, gamma = 90.0, 90.0, 90.0
    else:
        print("\nВведите параметры решетки:")
        a = float(input("Постоянная a (Å), по умолчанию 5.0: ") or "5.0")
        b = float(input("Постоянная b (Å), по умолчанию 5.0: ") or "5.0")
        c = float(input("Постоянная c (Å), по умолчанию 5.0: ") or "5.0")
        alpha = float(input("Угол α (градусы), по умолчанию 90.0: ") or "90.0")
        beta = float(input("Угол β (градусы), по умолчанию 90.0: ") or "90.0")
        gamma = float(input("Угол γ (градусы), по умолчанию 90.0: ") or "90.0")

    # Размеры решетки
    print("\nРазмеры решетки (сколько ионов по осям X, Y, Z):")

    use_preset = input("Использовать готовые размеры? (y/n), по умолчанию y: ").lower()

    if use_preset != 'n':
        print("\n1. Малая (3×3×3)")
        print("2. Средняя (5×5×5)")
        print("3. Большая (10×10×10)")
        print("4. Очень большая (20×20×20)")

        size_choice = input("\nВыбор (1-4), по умолчанию 2: ") or "2"

        size_map = {
            '1': (3, 3, 3),
            '2': (5, 5, 5),
            '3': (10, 10, 10),
            '4': (20, 20, 20)
        }
        nx, ny, nz = size_map.get(size_choice, (5, 5, 5))
    else:
        nx = int(input("Количество ионов по X: "))
        ny = int(input("Количество ионов по Y: "))
        nz = int(input("Количество ионов по Z: "))

    # Шум
    add_noise_input = input("\nДобавить шум к позициям атомов? (y/n), по умолчанию n: ").lower()
    add_noise = add_noise_input == 'y'
    noise_level = 0.05

    if add_noise:
        noise_level = float(input("Уровень шума (доля от a), по умолчанию 0.05: ") or "0.05")

    # Вакансии (дефекты)
    add_vacancies_input = input("\nДобавить вакансии (дефекты решетки)? (y/n), по умолчанию n: ").lower()
    add_vacancies = add_vacancies_input == 'y'
    vacancy_prob = 0.0

    if add_vacancies:
        vacancy_prob = float(input("Вероятность вакансии (0.01-0.5), по умолчанию 0.05: ") or "0.05")
        print(f"  → Примерно {vacancy_prob * 100:.1f}% атомов будут удалены")

    # Имя файла
    print()
    default_name = f"{lattice_type}_{nx}x{ny}x{nz}.xyz"
    filename = input(f"Имя выходного файла, по умолчанию '{default_name}': ") or default_name
    filepath = f"xyz_files/{filename}"

    # Генерация
    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ...")
    print("=" * 70)

    lattice = CrystalLattice(lattice_type, a, b, c, alpha, beta, gamma)

    print(f"\nТип решетки: {info['name']}")
    print(f"Параметры: a={lattice.a:.3f}, b={lattice.b:.3f}, c={lattice.c:.3f}")
    print(f"Углы: α={lattice.alpha:.1f}°, β={lattice.beta:.1f}°, γ={lattice.gamma:.1f}°")
    print(f"Размеры: {nx} × {ny} × {nz}")
    print(f"Шум: {'Да' if add_noise else 'Нет'}{f' (уровень {noise_level})' if add_noise else ''}")
    print(f"Вакансии: {'Да' if add_vacancies else 'Нет'}{f' (вероятность {vacancy_prob})' if add_vacancies else ''}")
    print()

    positions = generate_lattice_parallel(lattice, nx, ny, nz, add_noise, noise_level, vacancy_prob)

    save_xyz(filepath, positions, 'A')

    print(f"\n✓ Успешно сгенерировано {len(positions)} атомов")
    print(f"✓ Файл сохранен: {filepath}")

    input("\nНажмите Enter для продолжения...")


def generate_dataset():
    """Генерирует датасет из множества кристаллических решеток"""
    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ДАТАСЕТА")
    print("=" * 70)

    print("\nВыберите режим генерации датасета:")
    print("1. Кубические решетки - разные размеры и уровни шума")
    print("2. Все типы решеток Браве - полный набор")
    print("0. Назад в главное меню")

    mode = input("\nВаш выбор (0-2): ")

    if mode == '1':
        generate_ionic_dataset()
    elif mode == '2':
        generate_bravais_dataset()
    elif mode == '0':
        return
    else:
        print("\nНеверный выбор!")
        input("\nНажмите Enter для продолжения...")


def generate_ionic_dataset():
    """Генерирует датасет кристаллических решеток"""
    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ДАТАСЕТА КРИСТАЛЛИЧЕСКИХ РЕШЕТОК")
    print("=" * 70)

    import csv
    import time
    import numpy as np
    from datetime import datetime

    # Настройка параметров
    print("\nПараметры генерации:")
    print("1. Стандартный набор (быстро)")
    print("   • 3 размера: 3×3×3, 5×5×5, 10×10×10")
    print("   • 3 уровня шума: без шума, 0.05, 0.1")
    print("   • Всего: 9 файлов")
    print()
    print("2. Расширенный набор (1000 файлов)")
    print("   • 10 размеров: кубические и несимметричные")
    print("     (3×3×3, 5×5×5, 7×7×7, 10×10×10, 5×5×8, 8×8×5,")
    print("      6×8×10, 12×10×8, 15×15×15, 20×15×10)")
    print("   • 10 уровней шума: от 0.0 до 0.15")
    print("   • 10 вариаций для каждой комбинации")
    print("   • Всего: 1000 файлов (~5-15 минут)")
    print()
    print("3. Пользовательский набор")

    choice = input("\nВыбор (1-3), по умолчанию 1: ") or "1"

    if choice == '2':
        # Расширенный набор: 1000 файлов
        # 10 размеров × 10 уровней шума × 10 вариаций = 1000
        # Используем разные размеры: кубические и несимметричные
        sizes = [
            (3, 3, 3),  # Малая кубическая
            (5, 5, 5),  # Средняя кубическая
            (7, 7, 7),  # Кубическая
            (10, 10, 10),  # Большая кубическая
            (5, 5, 8),  # Вытянутая по Z
            (8, 8, 5),  # Сплющенная по Z
            (6, 8, 10),  # Несимметричная
            (12, 10, 8),  # Несимметричная обратная
            (15, 15, 15),  # Очень большая кубическая
            (20, 15, 10)  # Большая несимметричная
        ]
        noise_levels = [0.0, 0.02, 0.03, 0.05, 0.07, 0.08, 0.10, 0.12, 0.13, 0.15]
        n_variations = 10  # Количество вариаций для каждой комбинации
    elif choice == '3':
        print("\nВведите размеры:")
        print("Формат 1: Симметричные (например: 3,5,10) → 3×3×3, 5×5×5, 10×10×10")
        print("Формат 2: Несимметричные (например: 3x4x5,5x5x8) → 3×4×5, 5×5×8")
        size_input = input("Размеры: ")

        sizes = []
        for s in size_input.split(','):
            s = s.strip()
            if 'x' in s.lower():
                # Несимметричный формат: 3x4x5
                parts = s.lower().split('x')
                if len(parts) == 3:
                    sizes.append((int(parts[0]), int(parts[1]), int(parts[2])))
            else:
                # Симметричный формат: 5 → 5x5x5
                size = int(s)
                sizes.append((size, size, size))

        print("\nВведите уровни шума (через запятую, 0 = без шума):")
        noise_input = input("Уровни шума: ")
        noise_levels = [float(n.strip()) for n in noise_input.split(',')]

        n_variations = int(input("Количество вариаций для каждой комбинации, по умолчанию 1: ") or "1")
    else:
        sizes = [(3, 3, 3), (5, 5, 5), (10, 10, 10)]
        noise_levels = [0.0, 0.05, 0.1]
        n_variations = 1

    # Выбор типа решетки
    print("\nВыберите тип решетки:")
    print("1. cubic_primitive (Примитивная кубическая)")
    print("2. cubic_body (ОЦК)")
    print("3. cubic_face (ГЦК)")

    lattice_choice = input("\nВыбор (1-3), по умолчанию 1: ") or "1"

    lattice_map = {
        '1': 'cubic_primitive',
        '2': 'cubic_body',
        '3': 'cubic_face'
    }
    lattice_type = lattice_map.get(lattice_choice, 'cubic_primitive')

    # Опция вакансий
    add_vacancies_input = input("\nДобавить вакансии (дефекты решетки)? (y/n), по умолчанию n: ").lower()
    add_vacancies = add_vacancies_input == 'y'
    vacancy_prob = 0.0

    if add_vacancies:
        vacancy_prob = float(input("Вероятность вакансии (0.01-0.2), по умолчанию 0.05: ") or "0.05")
        print(f"  → Примерно {vacancy_prob * 100:.1f}% атомов будут удалены")

    # Создание папки для датасета
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dataset_dir = f"xyz_files/dataset_{lattice_type}_{timestamp}"
    os.makedirs(dataset_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ДАТАСЕТА...")
    print("=" * 70)
    print(f"\nПапка: {dataset_dir}")
    print(f"Тип решетки: {lattice_type}")
    print(f"Количество конфигураций: {len(sizes) * len(noise_levels) * n_variations}")
    if add_vacancies:
        print(f"Вакансии: Да (вероятность {vacancy_prob})")
    print()

    # Подготовка метаданных
    metadata = []

    # Генерация решеток
    total = len(sizes) * len(noise_levels) * n_variations
    current = 0

    start_time = time.time()

    # Создаем решетку заранее
    lattice = CrystalLattice(lattice_type)

    for nx, ny, nz in sizes:
        for noise_level in noise_levels:
            for variation in range(n_variations):
                current += 1

                # Формирование имени файла
                noise_str = "no_noise" if noise_level == 0.0 else f"noise_{noise_level:.2f}"

                if n_variations > 1:
                    # Если есть вариации, добавляем номер вариации
                    filename = f"{lattice_type}_{nx}x{ny}x{nz}_{noise_str}_v{variation + 1:03d}.xyz"
                else:
                    filename = f"{lattice_type}_{nx}x{ny}x{nz}_{noise_str}.xyz"

                filepath = os.path.join(dataset_dir, filename)

                # Компактный вывод прогресса
                if total <= 100 or current % 10 == 1 or current == total:
                    print(f"[{current}/{total}] {filename[:50]:50s}...", end=" ", flush=True)

                # Генерация позиций с уникальным seed для каждой вариации
                add_noise = noise_level > 0.0

                # Устанавливаем seed для воспроизводимости (но разный для каждой вариации)
                if add_noise or add_vacancies:
                    np.random.seed(int(time.time() * 1000) % (2 ** 32) + current)

                positions = generate_lattice_parallel(lattice, nx, ny, nz, add_noise, noise_level, vacancy_prob)

                # Сохранение - используем чередование A/B для атомов
                save_xyz(filepath, positions, 'A')  # Просто используем 'A' для всех атомов

                # Метаданные
                metadata.append({
                    'filename': filename,
                    'lattice_type': lattice_type,
                    'nx': nx,
                    'ny': ny,
                    'nz': nz,
                    'size': f"{nx}x{ny}x{nz}",
                    'noise_level': noise_level,
                    'noise_enabled': add_noise,
                    'vacancy_prob': vacancy_prob,
                    'vacancy_enabled': add_vacancies,
                    'variation': variation + 1 if n_variations > 1 else 1,
                    'num_atoms': len(positions),
                    'a': lattice.a,
                    'b': lattice.b,
                    'c': lattice.c,
                })

                if total <= 100 or current % 10 == 1 or current == total:
                    print("✓")

                # Промежуточная статистика каждые 100 файлов
                if current % 100 == 0 and current < total:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / current
                    remaining = (total - current) * avg_time
                    print(f"\n    Прогресс: {current}/{total} ({100 * current / total:.1f}%) | "
                          f"Времени прошло: {elapsed:.1f}с | "
                          f"Осталось: ~{remaining:.1f}с\n")

    elapsed = time.time() - start_time

    # Сохранение метаданных
    metadata_file = os.path.join(dataset_dir, 'metadata.csv')
    with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=metadata[0].keys())
        writer.writeheader()
        writer.writerows(metadata)

    # Сводка
    print("\n" + "=" * 70)
    print("ДАТАСЕТ УСПЕШНО СГЕНЕРИРОВАН!")
    print("=" * 70)
    print(f"\n✓ Папка: {dataset_dir}")
    print(f"✓ Количество файлов: {len(metadata)}")
    print(f"✓ Общее количество атомов: {sum(m['num_atoms'] for m in metadata):,}")
    print(f"✓ Время генерации: {elapsed:.2f} сек ({elapsed / 60:.2f} мин)")
    print(f"✓ Средняя скорость: {len(metadata) / elapsed:.2f} файлов/сек")
    print(f"✓ Метаданные сохранены: {metadata_file}")

    # Статистика по размерам
    if len(sizes) > 1:
        print("\nСтатистика по размерам:")
        size_stats = {}
        for m in metadata:
            size = m['size']
            size_stats[size] = size_stats.get(size, 0) + 1
        for size, count in sorted(size_stats.items()):
            print(f"  {size:10s}: {count:4d} файлов")

    # Статистика по шуму
    if len(noise_levels) > 1:
        print("\nСтатистика по уровню шума:")
        noise_stats = {}
        for m in metadata:
            noise = m['noise_level']
            noise_stats[noise] = noise_stats.get(noise, 0) + 1
        for noise, count in sorted(noise_stats.items()):
            noise_label = "без шума" if noise == 0.0 else f"шум {noise:.2f}"
            print(f"  {noise_label:12s}: {count:4d} файлов")

    input("\nНажмите Enter для продолжения...")


def generate_bravais_dataset():
    """Генерирует полный датасет всех типов решеток Браве"""
    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ВСЕХ РЕШЕТОК БРАВЕ")
    print("=" * 70)

    import csv
    import time

    print("\nЭта функция сгенерирует датасет из всех 14 типов решеток Браве.")

    # Настройка параметров
    print("\nПараметры генерации:")
    print("1. Минимальный набор (быстро)")
    print("   • 2 размера: 5×5×5, 10×10×10")
    print("   • 2 варианта: без шума и с шумом 0.05")
    print("   • 14 типов решеток")
    print("   • Всего: 56 файлов")
    print()
    print("2. Стандартный набор")
    print("   • 3 размера: 5×5×5, 10×10×10, 15×15×15")
    print("   • 3 варианта шума: без шума, 0.05, 0.1")
    print("   • 14 типов решеток")
    print("   • Всего: 126 файлов")
    print()
    print("3. Пользовательский набор")

    choice = input("\nВыбор (1-3), по умолчанию 1: ") or "1"

    if choice == '2':
        sizes = [(5, 5, 5), (10, 10, 10), (15, 15, 15)]
        noise_levels = [0.0, 0.05, 0.1]
    elif choice == '3':
        print("\nВведите размеры (через запятую, например: 5,10,15):")
        size_input = input("Размеры: ")
        sizes_list = [int(s.strip()) for s in size_input.split(',')]
        sizes = [(s, s, s) for s in sizes_list]

        print("\nВведите уровни шума (через запятую, 0 = без шума):")
        noise_input = input("Уровни шума: ")
        noise_levels = [float(n.strip()) for n in noise_input.split(',')]
    else:
        sizes = [(5, 5, 5), (10, 10, 10)]
        noise_levels = [0.0, 0.05]

    # Выбор элемента
    element = input("\nХимический элемент, по умолчанию C: ") or "C"

    # Создание папки для датасета
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dataset_dir = f"xyz_files/dataset_bravais_{element}_{timestamp}"
    os.makedirs(dataset_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ПОЛНОГО ДАТАСЕТА...")
    print("=" * 70)
    print(f"\nПапка: {dataset_dir}")
    print(f"Элемент: {element}")
    print(f"Типов решеток: 14")
    print(f"Конфигураций на тип: {len(sizes) * len(noise_levels)}")
    print(f"Всего файлов: {14 * len(sizes) * len(noise_levels)}")
    print()

    # Подготовка метаданных
    metadata = []

    # Генерация решеток
    all_lattice_types = list(CrystalLattice.LATTICE_TYPES.keys())
    total = len(all_lattice_types) * len(sizes) * len(noise_levels)
    current = 0

    start_time = time.time()

    for lattice_type in all_lattice_types:
        info = CrystalLattice.LATTICE_TYPES[lattice_type]

        for nx, ny, nz in sizes:
            for noise_level in noise_levels:
                current += 1

                # Формирование имени файла
                noise_str = "no_noise" if noise_level == 0.0 else f"noise_{noise_level:.2f}"
                filename = f"{lattice_type}_{nx}x{ny}x{nz}_{noise_str}.xyz"
                filepath = os.path.join(dataset_dir, filename)

                print(f"[{current}/{total}] {lattice_type:30s} {nx}x{ny}x{nz} {noise_str:12s}...", end=" ", flush=True)

                # Создание решетки
                lattice = CrystalLattice(lattice_type)

                # Генерация позиций
                add_noise = noise_level > 0.0
                positions = generate_lattice_parallel(lattice, nx, ny, nz, add_noise, noise_level)

                # Сохранение
                save_xyz(filepath, positions, element)

                # Метаданные
                metadata.append({
                    'filename': filename,
                    'lattice_type': lattice_type,
                    'lattice_name': info['name'],
                    'syngony': info['syngony'],
                    'centering': info['centering'],
                    'element': element,
                    'nx': nx,
                    'ny': ny,
                    'nz': nz,
                    'size': f"{nx}x{ny}x{nz}",
                    'noise_level': noise_level,
                    'noise_enabled': add_noise,
                    'num_atoms': len(positions),
                    'a': lattice.a,
                    'b': lattice.b,
                    'c': lattice.c,
                    'alpha': lattice.alpha,
                    'beta': lattice.beta,
                    'gamma': lattice.gamma,
                })

                print("✓")

    elapsed = time.time() - start_time

    # Сохранение метаданных
    metadata_file = os.path.join(dataset_dir, 'metadata.csv')
    with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=metadata[0].keys())
        writer.writeheader()
        writer.writerows(metadata)

    # Статистика по сингониям
    syngony_stats = {}
    for m in metadata:
        syngony = m['syngony']
        syngony_stats[syngony] = syngony_stats.get(syngony, 0) + 1

    # Сводка
    print("\n" + "=" * 70)
    print("ДАТАСЕТ УСПЕШНО СГЕНЕРИРОВАН!")
    print("=" * 70)
    print(f"\n✓ Папка: {dataset_dir}")
    print(f"✓ Количество файлов: {len(metadata)}")
    print(f"✓ Общее количество атомов: {sum(m['num_atoms'] for m in metadata):,}")
    print(f"✓ Время генерации: {elapsed:.2f} сек")
    print(f"✓ Метаданные сохранены: {metadata_file}")

    print("\nРаспределение по сингониям:")
    for syngony, count in sorted(syngony_stats.items()):
        print(f"  {syngony:15s}: {count:3d} файлов")

    input("\nНажмите Enter для продолжения...")


def show_info():
    """Показывает информацию о решетках"""
    print("\n" + "=" * 70)
    print("ИНФОРМАЦИЯ О РЕШЕТКАХ БРАВЕ")
    print("=" * 70)

    print("\n14 решеток Браве классифицируются по 7 сингониям:\n")

    info_data = {
        'Кубическая': {
            'ограничения': 'a = b = c, α = β = γ = 90°',
            'типы': ['Примитивная (P)', 'Объемно-центрированная (I)', 'Гране-центрированная (F)'],
            'примеры': 'Po, Fe, Al, Cu, Au'
        },
        'Тетрагональная': {
            'ограничения': 'a = b ≠ c, α = β = γ = 90°',
            'типы': ['Примитивная (P)', 'Объемно-центрированная (I)'],
            'примеры': 'Sn, TiO₂'
        },
        'Ромбическая': {
            'ограничения': 'a ≠ b ≠ c, α = β = γ = 90°',
            'типы': ['Примитивная (P)', 'Базо-центрированная (C)',
                     'Объемно-центрированная (I)', 'Гране-центрированная (F)'],
            'примеры': 'S, I₂, U'
        },
        'Гексагональная': {
            'ограничения': 'a = b ≠ c, α = β = 90°, γ = 120°',
            'типы': ['Примитивная (P)'],
            'примеры': 'Mg, Zn, C'
        },
        'Тригональная': {
            'ограничения': 'a = b = c, α = β = γ ≠ 90°',
            'типы': ['Ромбоэдрическая (R)'],
            'примеры': 'As, Sb, Bi, CaCO₃'
        },
        'Моноклинная': {
            'ограничения': 'a ≠ b ≠ c, α = γ = 90°, β ≠ 90°',
            'типы': ['Примитивная (P)', 'Базо-центрированная (C)'],
            'примеры': 'S, CaSO₄·2H₂O'
        },
        'Триклинная': {
            'ограничения': 'a ≠ b ≠ c, α ≠ β ≠ γ',
            'типы': ['Примитивная (P)'],
            'примеры': 'CuSO₄·5H₂O, K₂Cr₂O₇'
        }
    }

    for syngony, data in info_data.items():
        print(f"{syngony}:")
        print(f"  Ограничения: {data['ограничения']}")
        print(f"  Типы центрирования: {', '.join(data['типы'])}")
        print(f"  Примеры: {data['примеры']}")
        print()

    input("\nНажмите Enter для продолжения...")


def run_scalability_test():
    """Запускает тест масштабируемости с графиком"""
    print("\n" + "=" * 70)
    print("ТЕСТ МАСШТАБИРУЕМОСТИ")
    print("=" * 70)

    import time
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    total_cpus = os.cpu_count()
    print(f"\nДоступно ядер процессора: {total_cpus}")

    # Выбор теста
    print("\nВыберите конфигурацию теста:")
    print("1. Малая нагрузка (30×30×30 ионов) - тест overhead параллелизации")
    print("2. Средняя нагрузка (80×80×80 ионов) - оптимальный баланс")
    print("3. Пользовательский")

    test_choice = input("\nВаш выбор (1-3), по умолчанию 2: ") or "2"

    if test_choice == '1':
        nx, ny, nz = 30, 30, 30
        n_tests = 3
        test_name = "Малая нагрузка"
    elif test_choice == '3':
        print("\nВведите параметры:")
        nx = int(input("Размер по X (ионы), по умолчанию 80: ") or "80")
        ny = int(input("Размер по Y (ионы), по умолчанию 80: ") or "80")
        nz = int(input("Размер по Z (ионы), по умолчанию 80: ") or "80")
        n_tests = int(input("Количество тестов с разным шумом, по умолчанию 3: ") or "3")
        test_name = "Пользовательский"
    else:
        nx, ny, nz = 80, 80, 80
        n_tests = 3
        test_name = "Средняя нагрузка"

    # Используем половину доступных ядер
    max_processes = max(1, total_cpus // 2)

    # Рассчитываем количество атомов
    basis_count = 4
    total_atoms = nx * ny * nz * basis_count

    print(f"\nПараметры теста:")
    print(f"  Конфигурация: {test_name}")
    print(f"  Тип решетки: cubic_face (ГЦК)")
    print(f"  Размер: {nx}×{ny}×{nz} ионов")
    print(f"  Атомов: {total_atoms:,}")
    print(f"  Количество тестов (с разным шумом): {n_tests}")
    print(f"  Использовано потоков: {max_processes} из {total_cpus} доступных")
    print("\nТестирование производительности...")
    print("(Каждый тест генерирует решетку с новым случайным шумом)")
    print()

    # Создаем решетку заранее (чтобы избежать копирования)
    lattice = CrystalLattice('cubic_face', 5.0, 5.0, 5.0)

    # Массивы для хранения результатов
    num_processes = list(range(1, max_processes + 1))
    time_real = []
    speedup = []
    efficiency = []

    # Тестируем для каждого количества процессов
    for n_proc in num_processes:
        print(f"  Процессов: {n_proc}/{max_processes} ... ", end="", flush=True)

        total_time = 0

        # Проводим несколько тестов с разным шумом
        for test_num in range(n_tests):
            start_time = time.perf_counter()

            # Генерируем решетку с шумом (каждый раз новый шум!)
            positions = generate_lattice_parallel(
                lattice, nx, ny, nz,
                add_noise=True,
                noise_level=0.05,
                n_processes=n_proc
            )

            elapsed = time.perf_counter() - start_time
            total_time += elapsed

        avg_time = total_time / n_tests
        time_real.append(avg_time)

        print(f"Время: {avg_time:.3f} сек")

    # Вычисляем идеальное время (линейное ускорение)
    time_ideal = [time_real[0] / i for i in num_processes]

    # Вычисляем ускорение и эффективность
    speedup = [time_real[0] / t for t in time_real]
    efficiency = [s / n * 100 for s, n in zip(speedup, num_processes)]

    # Вывод результатов
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 70)
    print(f"\n{'Процессов':<12} {'Время (с)':<15} {'Ускорение':<15} {'Эффективность'}")
    print("-" * 70)

    for n, t_real, sp, eff in zip(num_processes, time_real, speedup, efficiency):
        print(f"{n:<12} {t_real:<15.3f} {sp:<15.2f}x {eff:<.1f}%")

    print("\n" + "=" * 70)
    print(f"Максимальное ускорение: {max(speedup):.2f}x при {num_processes[speedup.index(max(speedup))]} процессах")
    print(f"Средняя эффективность: {np.mean(efficiency):.1f}%")
    print("=" * 70)

    # Анализ результатов
    print("\n💡 АНАЛИЗ МАСШТАБИРУЕМОСТИ:")
    avg_eff = np.mean(efficiency)

    if avg_eff > 80:
        print("  ✅ ОТЛИЧНАЯ МАСШТАБИРУЕМОСТЬ!")
        print("     Параллельный алгоритм работает очень эффективно.")
        print("     Дальнейшее увеличение процессов даст хороший прирост.")
    elif avg_eff > 60:
        print("  ✓ ХОРОШАЯ МАСШТАБИРУЕМОСТЬ")
        print("     Параллелизм работает эффективно.")
        print("     Можно увеличивать количество процессов.")
    elif avg_eff > 40:
        print("  ⚠️  СРЕДНЯЯ МАСШТАБИРУЕМОСТЬ")
        print("     Есть некоторый overhead от параллелизации.")
        print("     Рекомендуется увеличить размер решетки.")
    else:
        print("  ❌ НИЗКАЯ МАСШТАБИРУЕМОСТЬ")
        print("     Overhead от параллелизации слишком велик.")
        print("     Рекомендации:")
        print("     - Увеличить размер решетки (минимум 150×150×30)")
        print("     - Использовать меньше процессов")

    print()

    # Построение ГРАФИКА МАСШТАБИРУЕМОСТИ
    fig, ax = plt.subplots(figsize=(12, 8))

    # Основной график масштабируемости
    ax.plot(num_processes, time_ideal,
            label="Идеальное ускорение (теоретический максимум)",
            linestyle="--", color="gray", linewidth=2.5, alpha=0.7)
    ax.plot(num_processes, time_real,
            label="Реальное ускорение",
            marker="o", color="red", linewidth=2.5, markersize=10)

    # Настройка графика
    ax.set_xlabel("Количество процессов", fontsize=14, fontweight='bold')
    ax.set_ylabel("Время выполнения (секунды)", fontsize=14, fontweight='bold')

    # Заголовок
    title_main = "Масштабируемость генератора кристаллических решеток"
    ax.set_title(title_main, fontsize=16, fontweight='bold', pad=15)

    # Подзаголовок внизу графика
    title_sub = f"{test_name}: {nx}×{ny}×{nz} ионов ГЦК, {total_atoms:,} атомов | {n_tests} теста с шумом | CPU: {max_processes}/{total_cpus} потоков"
    fig.text(0.5, 0.02, title_sub, ha='center', fontsize=11,
             bbox=dict(boxstyle='round,pad=0.7', facecolor='lightgray',
                       edgecolor='gray', alpha=0.8))

    # Добавляем линии сетки и настраиваем оси
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.set_xticks(num_processes)
    ax.tick_params(axis='both', labelsize=11)

    # Устанавливаем границы осей
    ax.set_xlim(0.5, max_processes + 0.5)
    ax.set_ylim(0, max(time_real) * 1.15)

    # Легенда
    ax.legend(fontsize=12, loc='upper right', framealpha=0.9)

    plt.tight_layout(rect=[0, 0.05, 1, 1])  # Оставляем место внизу для подзаголовка

    # Сохранение графика
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"scalability_tests/test_{timestamp}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')

    print(f"\n✓ График масштабируемости сохранен: {output_file}")
    print()

    plt.close()


def main():
    """Главная функция программы"""

    # Создаем папки для файлов
    ensure_directories()

    while True:
        print_header()
        print_menu()

        try:
            choice = input("\nВыберите действие: ")

            if choice == '1':
                single_generation()
            elif choice == '2':
                generate_dataset()
            elif choice == '3':
                run_scalability_test()
            elif choice == '4':
                show_info()
            elif choice == '0':
                print("\nДо свидания!")
                break
            else:
                print("\nНеверный выбор! Попробуйте снова.")

            if choice in ['1', '2']:
                input("\nНажмите Enter для продолжения...")

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"\nОшибка: {e}")
            input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()