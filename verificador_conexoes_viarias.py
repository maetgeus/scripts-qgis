# Verificador de Conexões Viárias
# Esse script analisa se os extremos das linhas da camada "Rotas Rurais" estão conectados à camada OSM

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QProgressDialog
)
from qgis.PyQt.QtCore import Qt, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsGeometry,
    QgsWkbTypes, QgsFeature, QgsField, QgsPointXY,
    QgsDistanceArea, QgsFeatureRequest
)

class TopologyChecker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verificador de Conexões Viárias")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()

        # ComboBox para escolher camada OSM
        layout.addWidget(QLabel("Camada OSM:"))
        self.cb_osm = QComboBox()
        self.load_layers(self.cb_osm)
        layout.addWidget(self.cb_osm)

        # ComboBox para escolher camada de Rotas Rurais
        layout.addWidget(QLabel("Camada Rotas Rurais:"))
        self.cb_rotas = QComboBox()
        self.load_layers(self.cb_rotas)
        layout.addWidget(self.cb_rotas)

        # Botão de execução
        self.btn_run = QPushButton("Executar")
        self.btn_run.clicked.connect(self.run_check)
        layout.addWidget(self.btn_run)

        self.setLayout(layout)

    def load_layers(self, combo_box):
        """Carrega no combo_box apenas camadas de linha"""
        combo_box.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.LineGeometry:
                combo_box.addItem(layer.name(), layer)

    def run_check(self):
        osm_layer = self.cb_osm.currentData()
        rotas_layer = self.cb_rotas.currentData()

        if not osm_layer or not rotas_layer:
            QMessageBox.warning(self, "Erro", "Selecione ambas as camadas!")
            return

        # Inicializa progresso
        total = rotas_layer.featureCount()
        progress = QProgressDialog("Analisando vias...", "Cancelar", 0, total, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        try:
            # Calculadora de distância
            d = QgsDistanceArea()
            d.setSourceCrs(osm_layer.crs(), QgsProject.instance().transformContext())

            # Camada de saída (pontos)
            vl = QgsVectorLayer(f"Point?crs={osm_layer.crs().authid()}", "conexoes_verificadas", "memory")
            pr = vl.dataProvider()
            pr.addAttributes([
                QgsField("id", QVariant.Int),
                QgsField("status", QVariant.String)
            ])
            vl.updateFields()

            features = []
            feature_id = 0

            # Percorre cada feição da camada de rotas
            for i, feature in enumerate(rotas_layer.getFeatures()):
                QCoreApplication.processEvents()
                if progress.wasCanceled():
                    return
                
                progress.setValue(i)
                progress.setLabelText(f"Analisando via {i + 1}/{total}")
                
                geom = feature.geometry()
                if geom.isEmpty():
                    continue

                # Para cada linha: pega ponto inicial e final
                for part in geom.constParts():
                    vertices = list(part.vertices())
                    if not vertices:
                        continue

                    for point in [vertices[0], vertices[-1]]:
                        qgs_point = QgsPointXY(point)
                        status = self.check_connection(qgs_point, osm_layer, d)

                        feat = QgsFeature()
                        feat.setGeometry(QgsGeometry.fromPointXY(qgs_point))
                        feat.setAttributes([feature_id, status])
                        features.append(feat)
                        feature_id += 1

            # Adiciona todos os pontos à camada
            pr.addFeatures(features)

            # Define estilo: vermelho
            renderer = vl.renderer()
            symbol = renderer.symbol()
            symbol.setColor(QColor(255, 0, 0))

            QgsProject.instance().addMapLayer(vl)
            progress.close()

            QMessageBox.information(
                self, "Concluído",
                f"Verificação finalizada!\n"
                f"Total de pontos analisados: {feature_id}"
            )

        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Erro", f"Falha na verificação:\n{str(e)}")

    def check_connection(self, point, osm_layer, distance_area):
        """Verifica se o ponto está conectado à rede OSM"""
        # Cria um retângulo de busca ao redor do ponto (raio 10m)
        request = QgsFeatureRequest()
        buffer = distance_area.measureLine([point, QgsPointXY(point.x() + 10, point.y())])
        rect = QgsGeometry.fromPointXY(point).boundingBox()
        rect.grow(buffer)
        request.setFilterRect(rect)

        for feature in osm_layer.getFeatures(request):
            if feature.geometry().distance(QgsGeometry.fromPointXY(point)) <= 10:
                return "Desconectado"

        return "Fim de rua"


# Executa o diálogo
dialog = TopologyChecker(iface.mainWindow())
dialog.exec_()
