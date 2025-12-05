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


if __name__ == "__main__":
    print("Используйте menu.py для запуска программы")