import PencilKit
import SwiftUI
import UIKit

struct DrawingCanvasView: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    let selectedColor: Color
    let strokeWidth: CGFloat
    let isEraser: Bool

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    func makeUIView(context: Context) -> PKCanvasView {
        let canvasView = PKCanvasView(frame: .zero)
        canvasView.backgroundColor = .clear
        canvasView.drawingPolicy = .anyInput
        canvasView.isOpaque = false
        canvasView.delegate = context.coordinator
        canvasView.alwaysBounceVertical = true
        canvasView.alwaysBounceHorizontal = true
        canvasView.minimumZoomScale = 1
        canvasView.maximumZoomScale = 1
        canvasView.showsVerticalScrollIndicator = false
        canvasView.showsHorizontalScrollIndicator = false
        canvasView.tool = context.coordinator.currentTool
        canvasView.drawing = drawing
        return canvasView
    }

    func updateUIView(_ uiView: PKCanvasView, context: Context) {
        context.coordinator.parent = self
        uiView.tool = context.coordinator.currentTool
        if uiView.drawing.dataRepresentation() != drawing.dataRepresentation() {
            uiView.drawing = drawing
        }
    }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        var parent: DrawingCanvasView

        init(parent: DrawingCanvasView) {
            self.parent = parent
        }

        var currentTool: PKTool {
            if parent.isEraser {
                return PKEraserTool(.vector)
            }
            return PKInkingTool(.pen, color: UIColor(parent.selectedColor), width: parent.strokeWidth)
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            parent.drawing = canvasView.drawing
        }
    }
}
