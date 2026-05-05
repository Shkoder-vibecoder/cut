from algorithms.base import BaseCuttingAlgorithm, Sheet, Piece, CuttingParams, CuttingResult, PlacementResult


class GreedyAlgorithm(BaseCuttingAlgorithm):
    def solve(self, sheets: list[Sheet], pieces: list[Piece], params: CuttingParams) -> CuttingResult:
        sorted_pieces = self._sort_pieces_by_area(pieces)
        placements = []
        sheet_states = []

        for s in sheets:
            for _ in range(getattr(s, 'quantity', 1)):
                sheet_states.append(SheetState(s.id, s.width, s.height, s.stock_sheet_id, s.texture))

        for piece in sorted_pieces:
            placed = False
            orientations = [(piece.width, piece.height)]
            if piece.rotation_allowed:
                orientations.append((piece.height, piece.width))

            for pw, ph in orientations:
                if piece.fibers != "any":
                    allowed_textures = ["none", piece.fibers]
                else:
                    allowed_textures = ["none", "horizontal", "vertical"]

                for state in sheet_states:
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
                    if pos is not None:
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
                        placed = True
                        break
                if placed:
                    break

        used_sheet_ids = set(p.sheet_id for p in placements)
        total_piece_area = sum(p.width * p.height for p in pieces)
        total_sheet_area = sum(s.width * s.height for s in sheet_states if s.sheet_id in used_sheet_ids)

        result = CuttingResult()
        result.placements = placements
        result.total_sheets_used = len(used_sheet_ids)
        result.kim_percent = (total_piece_area / total_sheet_area * 100) if total_sheet_area > 0 else 0.0
        result.status = "done"
        result.message = "Completed"
        return result

    def _find_position(self, state: "SheetState", pw: float, ph: float, params: CuttingParams) -> tuple[float, float] | None:
        step = 20.0
        min_x = int(params.edge_offset)
        min_y = int(params.edge_offset)
        max_x = int(state.width - pw - params.edge_offset)
        max_y = int(state.height - ph - params.edge_offset)
        if max_x < min_x or max_y < min_y:
            return None
        for x in range(min_x, max_x + 1, int(step)):
            for y in range(min_y, max_y + 1, int(step)):
                if state.can_place(x, y, pw, ph, params.cut_width, params.edge_offset):
                    return (float(x), float(y))
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
