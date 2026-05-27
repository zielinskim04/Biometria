import numpy as np
from collections import deque
from math import sqrt


class SkeletonRepair:
    """
    Naprawa i czyszczenie szkieletu po szkieletyzacji.

    Metody:
        remove_short  – usuwa krótkie komponenty (szum/ostrogi)
        reconnect     – łączy bliskie zakończenia o zgodnym kierunku
        clean         – remove_short + reconnect w jednym wywołaniu
    """

    # ------------------------------------------------------------------ #
    # Wewnętrzne                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_endpoints(skeleton: np.ndarray) -> list:
        """Zwraca listę (r, c, neighbor) dla każdego zakończenia szkieletu."""
        endpoints = []
        rows, cols = skeleton.shape
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if skeleton[r, c] != 1: continue
                neighbors = [
                    (r + dy, c + dx)
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                    if not (dy == 0 and dx == 0)
                    if skeleton[r + dy, c + dx] == 1
                ]
                if len(neighbors) == 1:
                    endpoints.append((r, c, neighbors[0]))
        return endpoints

    @staticmethod
    def _draw_line(img: np.ndarray,
                   x1: int, y1: int,
                   x2: int, y2: int,
                   value: int = 1) -> None:
        """Rysuje linię algorytmem Bresenhama (in-place)."""
        dx = abs(x2 - x1); dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            img[y1, x1] = value
            if x1 == x2 and y1 == y2: break
            e2 = 2 * err
            if e2 > -dy: err -= dy; x1 += sx
            if e2 <  dx: err += dx; y1 += sy

    def remove_short(self, skeleton: np.ndarray,
                     min_length: int = 10) -> np.ndarray:
        """
        Usuwa komponenty spójne szkieletu krótsze niż min_length pikseli.

        Eliminuje szum i bardzo krótkie ostrogi powstałe po szkieletyzacji.
        """
        cleaned = skeleton.copy()
        rows, cols = cleaned.shape
        visited    = np.zeros_like(cleaned, dtype=bool)
        dirs       = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

        for r in range(rows):
            for c in range(cols):
                if cleaned[r, c] != 1 or visited[r, c]: continue
                queue     = deque([(r, c)])
                component = []
                visited[r, c] = True
                while queue:
                    y, x = queue.popleft()
                    component.append((y, x))
                    for dy, dx in dirs:
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < rows and 0 <= nx < cols and
                                cleaned[ny, nx] == 1 and not visited[ny, nx]):
                            visited[ny, nx] = True
                            queue.append((ny, nx))
                if len(component) < min_length:
                    for y, x in component:
                        cleaned[y, x] = 0
        return cleaned

    def reconnect(self, skeleton: np.ndarray,
                  max_distance: int = 8) -> np.ndarray:
        """
        Łączy bliskie zakończenia grzbietów o zbieżnym kierunku.

        Warunki połączenia:
        – odległość ≤ max_distance pikseli,
        – iloczyn skalarny kierunków obydwu zakończeń z wektorem łączącym > 0.8.
        """
        repaired  = skeleton.copy()
        endpoints = self._find_endpoints(repaired)

        for i in range(len(endpoints)):
            y1, x1, n1 = endpoints[i]
            dy1 = y1 - n1[0]; dx1 = x1 - n1[1]

            for j in range(i + 1, len(endpoints)):
                y2, x2, n2 = endpoints[j]
                dy2 = y2 - n2[0]; dx2 = x2 - n2[1]

                dist = sqrt((x2-x1)**2 + (y2-y1)**2)
                if dist > max_distance: continue

                vx = (x2 - x1) / dist
                vy = (y2 - y1) / dist

                d1 = sqrt(dx1**2 + dy1**2)
                d2 = sqrt(dx2**2 + dy2**2)
                if d1 == 0 or d2 == 0: continue

                dot1 = (dx1/d1)*vx + (dy1/d1)*vy
                dot2 = -(dx2/d2)*vx - (dy2/d2)*vy

                if dot1 > 0.8 and dot2 > 0.8:
                    self._draw_line(repaired, x1, y1, x2, y2)
        return repaired

    def clean(self, skeleton: np.ndarray,
              min_length:   int = 10,
              max_distance: int = 8) -> np.ndarray:
        """
        Pełne czyszczenie: remove_short → reconnect → remove_short.

        Drugie remove_short usuwa krótkie linie które mogły się pojawić
        po reconnect w przypadku fałszywych połączeń.
        """
        s = self.reconnect(skeleton, max_distance)
        s = self.remove_short(s, min_length)
        #s = self.reconnect(s, max_distance)
        #s = self.remove_short(s, min_length)
        return s
