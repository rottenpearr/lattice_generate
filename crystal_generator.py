#!/usr/bin/env python3
"""
Генератор кристаллических решеток с поддержкой мультипроцессинга
Поддерживает различные типы решеток Браве и сингонии
"""

import numpy as np
from multiprocessing import Pool, cpu_count
from typing import Tuple, List, Optional
import argparse
from pathlib import Path


class CrystalLattice:
    """Базовый класс для генерации кристаллических решеток"""

    # Определение параметров для различных сингоний
    LATTICE_TYPES = {
        # Триклинная сингония
        'triclinic_primitive': {
            'name': 'Триклинная примитивная',
            'syngony': 'triclinic',
            'centering': 'P'
        },

        # Моноклинная сингония
        'monoclinic_primitive': {
            'name': 'Моноклинная примитивная',
            'syngony': 'monoclinic',
            'centering': 'P'
        },
        'monoclinic_base': {
            'name': 'Моноклинная базо-центрированная',
            'syngony': 'monoclinic',
            'centering': 'C'
        },

        # Ромбическая сингония (орторомбическая)
        'orthorhombic_primitive': {
            'name': 'Ромбическая примитивная',
            'syngony': 'orthorhombic',
            'centering': 'P'
        },
        'orthorhombic_base': {
            'name': 'Ромбическая базо-центрированная',
            'syngony': 'orthorhombic',
            'centering': 'C'
        },
        'orthorhombic_body': {
            'name': 'Ромбическая объемно-центрированная',
            'syngony': 'orthorhombic',
            'centering': 'I'
        },
        'orthorhombic_face': {
            'name': 'Ромбическая гране-центрированная',
            'syngony': 'orthorhombic',
            'centering': 'F'
        },

        # Тетрагональная сингония
        'tetragonal_primitive': {
            'name': 'Тетрагональная примитивная',
            'syngony': 'tetragonal',
            'centering': 'P'
        },
        'tetragonal_body': {
            'name': 'Тетрагональная объемно-центрированная',
            'syngony': 'tetragonal',
            'centering': 'I'
        },

        # Гексагональная сингония
        'hexagonal': {
            'name': 'Гексагональная',
            'syngony': 'hexagonal',
            'centering': 'P'
        },

        # Тригональная сингония (ромбоэдрическая)
        'trigonal_rhombohedral': {
            'name': 'Тригональная ромбоэдрическая',
            'syngony': 'trigonal',
            'centering': 'R'
        },

        # Кубическая сингония
        'cubic_primitive': {
            'name': 'Кубическая примитивная',
            'syngony': 'cubic',
            'centering': 'P'
        },
        'cubic_body': {
            'name': 'Кубическая объемно-центрированная (ОЦК)',
            'syngony': 'cubic',
            'centering': 'I'
        },
        'cubic_face': {
            'name': 'Кубическая гране-центрированная (ГЦК)',
            'syngony': 'cubic',
            'centering': 'F'
        },
    }

    def __init__(self, lattice_type: str, a: float = 5.0, b: float = 5.0,
                 c: float = 5.0, alpha: float = 90.0, beta: float = 90.0,
                 gamma: float = 90.0):
        """
        Инициализация решетки

        Args:
            lattice_type: Тип решетки
            a, b, c: Постоянные решетки (в ангстремах)
            alpha, beta, gamma: Углы (в градусах)
        """
        if lattice_type not in self.LATTICE_TYPES:
            raise ValueError(f"Неизвестный тип решетки: {lattice_type}")

        self.lattice_type = lattice_type
        self.info = self.LATTICE_TYPES[lattice_type]

        # Применение ограничений сингонии
        self.a, self.b, self.c, self.alpha, self.beta, self.gamma = \
            self._apply_syngony_constraints(
                self.info['syngony'], a, b, c, alpha, beta, gamma
            )

    def _apply_syngony_constraints(self, syngony: str, a: float, b: float,
                                   c: float, alpha: float, beta: float,
                                   gamma: float) -> Tuple[float, ...]:
        """Применяет ограничения симметрии для данной сингонии"""

        if syngony == 'cubic':
            # a = b = c, α = β = γ = 90°
            return a, a, a, 90.0, 90.0, 90.0

        elif syngony == 'tetragonal':
            # a = b ≠ c, α = β = γ = 90°
            return a, a, c, 90.0, 90.0, 90.0

        elif syngony == 'orthorhombic':
            # a ≠ b ≠ c, α = β = γ = 90°
            return a, b, c, 90.0, 90.0, 90.0

        elif syngony == 'hexagonal':
            # a = b ≠ c, α = β = 90°, γ = 120°
            return a, a, c, 90.0, 90.0, 120.0

        elif syngony == 'trigonal':
            # a = b = c, α = β = γ ≠ 90°
            return a, a, a, alpha, alpha, alpha

        elif syngony == 'monoclinic':
            # a ≠ b ≠ c, α = γ = 90°, β ≠ 90°
            return a, b, c, 90.0, beta, 90.0

        elif syngony == 'triclinic':
            # a ≠ b ≠ c, α ≠ β ≠ γ ≠ 90°
            return a, b, c, alpha, beta, gamma

        return a, b, c, alpha, beta, gamma

    def get_lattice_vectors(self) -> np.ndarray:
        """Возвращает векторы элементарной ячейки"""
        alpha_rad = np.radians(self.alpha)
        beta_rad = np.radians(self.beta)
        gamma_rad = np.radians(self.gamma)

        # Вектор a направлен вдоль оси x
        ax = self.a
        ay = 0
        az = 0

        # Вектор b лежит в плоскости xy
        bx = self.b * np.cos(gamma_rad)
        by = self.b * np.sin(gamma_rad)
        bz = 0

        # Вектор c
        cx = self.c * np.cos(beta_rad)
        cy = self.c * (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad)
        cz = np.sqrt(self.c**2 - cx**2 - cy**2)

        return np.array([
            [ax, ay, az],
            [bx, by, bz],
            [cx, cy, cz]
        ])

    def get_basis_positions(self) -> List[np.ndarray]:
        """Возвращает позиции атомов в элементарной ячейке (в долях)"""
        centering = self.info['centering']

        positions = [np.array([0.0, 0.0, 0.0])]  # Примитивный узел

        if centering == 'I':  # Body-centered (объемно-центрированная)
            positions.append(np.array([0.5, 0.5, 0.5]))

        elif centering == 'F':  # Face-centered (гране-центрированная)
            positions.extend([
                np.array([0.5, 0.5, 0.0]),
                np.array([0.5, 0.0, 0.5]),
                np.array([0.0, 0.5, 0.5])
            ])

        elif centering == 'C':  # Base-centered (базо-центрированная)
            positions.append(np.array([0.5, 0.5, 0.0]))

        elif centering == 'R':  # Rhombohedral (ромбоэдрическая)
            positions.extend([
                np.array([1/3, 2/3, 2/3]),
                np.array([2/3, 1/3, 1/3])
            ])

        return positions

    def generate_lattice(self, nx: int, ny: int, nz: int,
                        add_noise: bool = False,
                        noise_level: float = 0.05) -> np.ndarray:
        """
        Генерирует координаты атомов решетки

        Args:
            nx, ny, nz: Количество элементарных ячеек вдоль каждой оси
            add_noise: Добавлять ли шум к позициям
            noise_level: Уровень шума (доля от постоянной решетки)

        Returns:
            Массив координат атомов формы (N, 3)
        """
        lattice_vectors = self.get_lattice_vectors()
        basis_positions = self.get_basis_positions()

        positions = []

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    cell_origin = i * lattice_vectors[0] + \
                                j * lattice_vectors[1] + \
                                k * lattice_vectors[2]

                    for basis_pos in basis_positions:
                        atom_pos = cell_origin + \
                                 basis_pos[0] * lattice_vectors[0] + \
                                 basis_pos[1] * lattice_vectors[1] + \
                                 basis_pos[2] * lattice_vectors[2]

                        if add_noise:
                            noise = np.random.normal(0, noise_level * self.a, 3)
                            atom_pos += noise

                        positions.append(atom_pos)

        return np.array(positions)


def generate_chunk(args):
    """Функция для генерации части решетки (для мультипроцессинга)"""
    lattice, nx, ny, nz_start, nz_end, add_noise, noise_level = args

    # Генерируем только часть решетки по оси z
    lattice_vectors = lattice.get_lattice_vectors()
    basis_positions = lattice.get_basis_positions()

    positions = []

    for i in range(nx):
        for j in range(ny):
            for k in range(nz_start, nz_end):
                cell_origin = i * lattice_vectors[0] + \
                            j * lattice_vectors[1] + \
                            k * lattice_vectors[2]

                for basis_pos in basis_positions:
                    atom_pos = cell_origin + \
                             basis_pos[0] * lattice_vectors[0] + \
                             basis_pos[1] * lattice_vectors[1] + \
                             basis_pos[2] * lattice_vectors[2]

                    if add_noise:
                        noise = np.random.normal(0, noise_level * lattice.a, 3)
                        atom_pos += noise

                    positions.append(atom_pos)

    return np.array(positions)


def generate_lattice_parallel(lattice: CrystalLattice, nx: int, ny: int, nz: int,
                              add_noise: bool = False, noise_level: float = 0.05,
                              n_processes: Optional[int] = None) -> np.ndarray:
    """
    Генерирует решетку с использованием мультипроцессинга

    Args:
        lattice: Объект решетки
        nx, ny, nz: Размеры решетки
        add_noise: Добавлять ли шум
        noise_level: Уровень шума
        n_processes: Количество процессов (None = все доступные ядра)
    """
    if n_processes is None:
        n_processes = cpu_count()

    # Разбиваем работу по оси z
    chunk_size = max(1, nz // n_processes)
    chunks = []

    for i in range(n_processes):
        nz_start = i * chunk_size
        nz_end = nz if i == n_processes - 1 else (i + 1) * chunk_size

        if nz_start < nz:
            chunks.append((lattice, nx, ny, nz_start, nz_end, add_noise, noise_level))

    # Генерируем части решетки параллельно
    with Pool(processes=n_processes) as pool:
        results = pool.map(generate_chunk, chunks)

    # Объединяем результаты
    positions = np.vstack(results)

    return positions


def generate_chunk_optimized(args):
    """Оптимизированная версия без передачи объекта lattice"""
    (lattice_type, a, b, c, alpha, beta, gamma), nx, ny, nz_start, nz_end, add_noise, noise_level = args

    # Воссоздаем lattice внутри процесса
    lattice = CrystalLattice(lattice_type, a, b, c, alpha, beta, gamma)
    lattice_vectors = lattice.get_lattice_vectors()
    basis_positions = lattice.get_basis_positions()

    # Предварительное вычисление
    positions = []
    basis_count = len(basis_positions)

    # Предварительное выделение памяти
    total_atoms = nx * ny * (nz_end - nz_start) * basis_count
    positions = np.zeros((total_atoms, 3))

    idx = 0
    for i in range(nx):
        for j in range(ny):
            for k in range(nz_start, nz_end):
                cell_origin = i * lattice_vectors[0] + \
                              j * lattice_vectors[1] + \
                              k * lattice_vectors[2]

                for basis_pos in basis_positions:
                    atom_pos = cell_origin + \
                               basis_pos[0] * lattice_vectors[0] + \
                               basis_pos[1] * lattice_vectors[1] + \
                               basis_pos[2] * lattice_vectors[2]

                    if add_noise:
                        noise = np.random.normal(0, noise_level * lattice.a, 3)
                        atom_pos += noise

                    positions[idx] = atom_pos
                    idx += 1

    return positions


def create_ionic_lattice(positions: np.ndarray, ion_types: List[str]) -> List[str]:
    """
    Создает список элементов для ионной решетки (например, NaCl)
    Чередует ионы в зависимости от позиции

    Args:
        positions: Массив координат атомов
        ion_types: Список типов ионов, например ['Na', 'Cl']

    Returns:
        Список элементов для каждого атома
    """
    if len(ion_types) == 1:
        return [ion_types[0]] * len(positions)

    elements = []
    for i in range(len(positions)):
        # Чередуем ионы
        elements.append(ion_types[i % len(ion_types)])

    return elements


def save_ionic_lattice(filename: str, positions: np.ndarray, ion_types: List[str]):
    """
    Сохраняет ионную решетку с чередующимися типами ионов

    Args:
        filename: Имя файла
        positions: Массив координат
        ion_types: Список типов ионов (например, ['Na', 'Cl'])
    """
    elements = create_ionic_lattice(positions, ion_types)
    save_xyz(filename, positions, elements=elements)


def save_xyz(filename: str, positions: np.ndarray, element: str = 'C', elements: list = None):
    """
    Сохраняет координаты в формате XYZ

    Args:
        filename: Имя файла
        positions: Массив координат
        element: Химический символ элемента (если один тип)
        elements: Список элементов для каждого атома (если несколько типов)
    """
    n_atoms = len(positions)

    with open(filename, 'w') as f:
        f.write(f"{n_atoms}\n")
        f.write(f"Crystal lattice generated\n")

        if elements is not None and len(elements) == n_atoms:
            # Используем разные элементы для каждого атома
            for pos, elem in zip(positions, elements):
                f.write(f"{elem} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")
        else:
            # Используем один элемент для всех атомов
            for pos in positions:
                f.write(f"{element} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")

    print(f"Сохранено {n_atoms} атомов в файл {filename}")


def interactive_mode():
    """Интерактивный режим работы программы"""
    print("=" * 70)
    print("ГЕНЕРАТОР КРИСТАЛЛИЧЕСКИХ РЕШЕТОК")
    print("=" * 70)
    print()

    # Показываем доступные типы решеток
    print("Доступные типы решеток:")
    print()

    lattice_list = list(CrystalLattice.LATTICE_TYPES.items())
    for idx, (key, info) in enumerate(lattice_list, 1):
        print(f"{idx:2d}. {info['name']} ({key})")

    print()

    # Выбор типа решетки
    while True:
        try:
            choice = int(input(f"Выберите тип решетки (1-{len(lattice_list)}): "))
            if 1 <= choice <= len(lattice_list):
                lattice_type = lattice_list[choice - 1][0]
                break
            else:
                print("Неверный выбор!")
        except ValueError:
            print("Введите число!")

    print()

    # Параметры решетки
    print("Параметры решетки (нажмите Enter для значений по умолчанию):")

    a = float(input("Постоянная a (Å) [5.0]: ") or "5.0")
    b = float(input("Постоянная b (Å) [5.0]: ") or "5.0")
    c = float(input("Постоянная c (Å) [5.0]: ") or "5.0")

    alpha = float(input("Угол α (градусы) [90.0]: ") or "90.0")
    beta = float(input("Угол β (градусы) [90.0]: ") or "90.0")
    gamma = float(input("Угол γ (градусы) [90.0]: ") or "90.0")

    print()

    # Размеры решетки
    print("Размеры решетки (количество элементарных ячеек):")
    nx = int(input("Размер по X: "))
    ny = int(input("Размер по Y: "))
    nz = int(input("Размер по Z: "))

    print()

    # Шум
    add_noise_input = input("Добавить шум к позициям атомов? (y/n) [n]: ").lower()
    add_noise = add_noise_input == 'y'

    noise_level = 0.05
    if add_noise:
        noise_level = float(input("Уровень шума (доля от постоянной решетки) [0.05]: ") or "0.05")

    print()

    # Выбор элемента
    print("\nТипы ионов:")
    print("1. Один элемент (например, C)")
    print("2. Ионная решетка (катионы и анионы)")

    ion_choice = input("\nВыбор (1-2) [1]: ") or "1"

    if ion_choice == '2':
        print("\nВведите катион (положительный ион):")
        cation = input("  Катион (например, Na, Ca, Li): ")
        print("\nВведите анион (отрицательный ион):")
        anion = input("  Анион (например, Cl, O, F): ")

        print("\nТип соединения:")
        print("1. AB (1:1) - например, NaCl, MgO")
        print("2. AB₂ (1:2) - например, CaF₂")
        print("3. A₂B (2:1) - например, Na₂O")

        compound_type = input("\nВыбор (1-3) [1]: ") or "1"

        if compound_type == '2':
            ion_types = [cation, anion, anion]
            formula = f"{cation}{anion}2"
        elif compound_type == '3':
            ion_types = [cation, cation, anion]
            formula = f"{cation}2{anion}"
        else:
            ion_types = [cation, anion]
            formula = f"{cation}{anion}"

        print(f"\nФормула соединения: {formula}")
    else:
        element = input("Химический символ элемента [C]: ") or "C"
        ion_types = [element]
        formula = element

    print()

    # Имя файла
    if len(ion_types) == 1:
        default_name = f"{lattice_type}_{nx}x{ny}x{nz}.xyz"
    else:
        default_name = f"{lattice_type}_{formula}_{nx}x{ny}x{nz}.xyz"

    filename = input(f"Имя выходного файла [{default_name}]: ") or default_name

    print()
    print("=" * 70)
    print("ГЕНЕРАЦИЯ...")
    print("=" * 70)

    # Создание решетки
    lattice = CrystalLattice(lattice_type, a, b, c, alpha, beta, gamma)

    print(f"Тип решетки: {lattice.info['name']}")
    print(f"Сингония: {lattice.info['syngony']}")
    print(f"Тип центрирования: {lattice.info['centering']}")
    print(f"Параметры: a={lattice.a:.3f}, b={lattice.b:.3f}, c={lattice.c:.3f}")
    print(f"Углы: α={lattice.alpha:.1f}°, β={lattice.beta:.1f}°, γ={lattice.gamma:.1f}°")
    print(f"Размеры: {nx} × {ny} × {nz}")
    print(f"Использование процессоров: {cpu_count()} ядер")
    print()

    # Генерация
    positions = generate_lattice_parallel(
        lattice, nx, ny, nz, add_noise, noise_level
    )

    # Сохранение
    if len(ion_types) == 1:
        save_xyz(filename, positions, ion_types[0])
    else:
        save_ionic_lattice(filename, positions, ion_types)

    print()
    print("Готово!")


def main():
    parser = argparse.ArgumentParser(
        description='Генератор кристаллических решеток с поддержкой мультипроцессинга'
    )

    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Интерактивный режим')
    parser.add_argument('--lattice-type', '-t', type=str,
                       help='Тип решетки')
    parser.add_argument('--size', '-s', type=int, nargs=3, metavar=('NX', 'NY', 'NZ'),
                       help='Размеры решетки')
    parser.add_argument('--params', '-p', type=float, nargs=6,
                       metavar=('a', 'b', 'c', 'alpha', 'beta', 'gamma'),
                       help='Параметры решетки')
    parser.add_argument('--noise', action='store_true',
                       help='Добавить шум')
    parser.add_argument('--noise-level', type=float, default=0.05,
                       help='Уровень шума (по умолчанию: 0.05)')
    parser.add_argument('--element', '-e', type=str, default='C',
                       help='Химический символ элемента (по умолчанию: C)')
    parser.add_argument('--output', '-o', type=str,
                       help='Имя выходного файла')
    parser.add_argument('--list-types', '-l', action='store_true',
                       help='Показать доступные типы решеток')

    args = parser.parse_args()

    if args.list_types:
        print("Доступные типы решеток:")
        for key, info in CrystalLattice.LATTICE_TYPES.items():
            print(f"  {key:30s} - {info['name']}")
        return

    if args.interactive or not args.lattice_type:
        interactive_mode()
    else:
        # Командная строка
        if not args.size:
            print("Ошибка: необходимо указать размеры решетки (--size)")
            return

        nx, ny, nz = args.size

        if args.params:
            a, b, c, alpha, beta, gamma = args.params
        else:
            a, b, c = 5.0, 5.0, 5.0
            alpha, beta, gamma = 90.0, 90.0, 90.0

        lattice = CrystalLattice(args.lattice_type, a, b, c, alpha, beta, gamma)

        positions = generate_lattice_parallel(
            lattice, nx, ny, nz, args.noise, args.noise_level
        )

        output_file = args.output or f"{args.lattice_type}_{nx}x{ny}x{nz}.xyz"
        save_xyz(output_file, positions, args.element)


if __name__ == "__main__":
    main()
