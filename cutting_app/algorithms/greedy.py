from algorithms.base import BaseCuttingAlgorithm, Sheet, Piece, CuttingParams, CuttingResult, PlacementResult


class GreedyAlgorithm(BaseCuttingAlgorithm):
    def solve(self, sheets: list[Sheet], pieces: list[Piece], params: CuttingParams) -> CuttingResult:
        sorted_pieces = self._sort_pieces_by_area(pieces)
        placements = []
        sheet_states = []
        used_state_indices = set()

        for s in sheets:
            for _ in range(getattr(s, 'quantity', 1)):
                sheet_states.append(SheetState(s.id, s.width, s.height, s.stock_sheet_id, s.texture))

        for piece in sorted_pieces:
            orientations = [(piece.width, piece.height)]
            if piece.rotation_allowed:
                orientations.append((piece.height, piece.width))
            if piece.fibers != "any":
                allowed_textures = ["none", piece.fibers]
            else:
                allowed_textures = ["none", "horizontal", "vertical"]

            best_candidate = None
            best_score = None

            for pw, ph in orientations:
                for state_idx, state in enumerate(sheet_states):
                    if state.texture not in allowed_textures:
                        continue

                    if params.cut_type == "guillotine" and not state.can_place_guillotine(
                        pw,
                        ph,
                        params.cut_width,
                        params.edge_offset,
                        params.max_guillotine_depth,
                    ):
                        continue

                    pos = self._find_position(state, pw, ph, params)
                    if pos is None:
                        continue

                    score = (state_idx, pos[1], pos[0], abs(pw - ph))
                    if best_score is None or score < best_score:
                        best_score = score
                        best_candidate = (state_idx, state, pos, pw, ph)

            if best_candidate is not None:
                state_idx, state, pos, pw, ph = best_candidate
                placement = PlacementResult(
                    piece_id=piece.id,
                    sheet_id=state.sheet_id,
                    x=pos[0],
                    y=pos[1],
                    width=pw,
                    height=ph,
                    rotated=(pw != piece.width)
                )
                placements.append(placement)
                state.add_placement(pos[0], pos[1], pw, ph, params.cut_width)
                used_state_indices.add(state_idx)

        total_piece_area = sum(p.width * p.height for p in pieces)
        total_sheet_area = sum(
            sheet_states[idx].width * sheet_states[idx].height for idx in used_state_indices
        )

        result = CuttingResult()
        result.placements = placements
        result.total_sheets_used = len(used_state_indices)
        result.kim_percent = (total_piece_area / total_sheet_area * 100) if total_sheet_area > 0 else 0.0
        result.status = "done"
        result.message = "Completed"
        return result

    def _find_position(self, state: "SheetState", pw: float, ph: float, params: CuttingParams) -> tuple[float, float] | None:
        min_x = float(params.edge_offset)
        min_y = float(params.edge_offset)
        max_x = float(state.width - pw - params.edge_offset)
        max_y = float(state.height - ph - params.edge_offset)
        if max_x < min_x or max_y < min_y:
            return None

        candidate_x = {min_x}
        candidate_y = {min_y}
        for px, py, placed_w, placed_h in state.placements:
            candidate_x.add(px + placed_w + params.cut_width)
            candidate_y.add(py + placed_h + params.cut_width)

        sorted_x = sorted(x for x in candidate_x if min_x <= x <= max_x)
        sorted_y = sorted(y for y in candidate_y if min_y <= y <= max_y)

        best_pos = None
        best_score = None
        for y in sorted_y:
            for x in sorted_x:
                if not state.can_place(x, y, pw, ph, params.cut_width, params.edge_offset):
                    continue
                # Lower score is better: keep pieces compact in top-left area.
                score = y * 1_000_000 + x
                if best_score is None or score < best_score:
                    best_score = score
                    best_pos = (x, y)

        if best_pos is not None:
            return best_pos
        return None


class SheetState:
    def __init__(self, sheet_id: int, width: float, height: float, stock_sheet_id: int, texture: str = "none"):
        self.sheet_id = sheet_id
        self.width = width
        self.height = height
        self.stock_sheet_id = stock_sheet_id
        self.texture = texture
        self.placements = []

    def can_place(self, x: float, y: float, w: float, h: float, cut_width: float, edge_offset: float) -> bool:
        if x + w + edge_offset > self.width or y + h + edge_offset > self.height:
            return False
        for px, py, pw, ph in self.placements:
            if not (x + w + cut_width <= px or
                    x >= px + pw + cut_width or
                    y + h + cut_width <= py or
                    y >= py + ph + cut_width):
                return False
        return True

    def add_placement(self, x: float, y: float, w: float, h: float, cut_width: float):
        self.placements.append((x, y, w, h))

    def can_place_guillotine(
        self,
        w: float,
        h: float,
        cut_width: float,
        edge_offset: float,
        max_guillotine_depth: float,
    ) -> bool:
        if h > max_guillotine_depth:
            return False

        if not self.placements:
            return self.can_place(edge_offset, edge_offset, w, h, cut_width, edge_offset)

        for px, py, pw, ph in self.placements:
            right_x = px + pw + cut_width
            if self.can_place(right_x, py, w, h, cut_width, edge_offset):
                return True
            top_y = py + ph + cut_width
            if self.can_place(px, top_y, w, h, cut_width, edge_offset):
                return True
        return False
