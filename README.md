# 🛠️ Automações QGIS

Repositório com scripts e códigos que desenvolvi para automatizar tarefas dentro do QGIS usando Python. A ideia é facilitar fluxos de trabalho no dia a dia com geoprocessamento, edição e análise espacial.

---

## 📌 Scripts disponíveis

### Verificador de Conexões Viárias (`verificador_conexoes_viarias.py`)
Esse script compara camadas de vias (como OpenStreetMap e Rotas Rurais) e identifica possíveis desconexões nas extremidades de linhas.

**Funcionalidades:**
- Interface simples com seleção de camadas
- Identifica os nós da camada Rotas Rurais e compara se está conectada à malha do Open Street Maps
- Resultado armazenado como camada temporária
- Pontos com Status "Fim de linha", para identificar ruas sem saída; e "Desconectado", para identificar ruas que não estão devidamente conectadas à malha

**Objetivo**
- Ajuda a corrigir manualmente quando temos duas camadas diferentes com vias que deveriam estar conectadas
- Correção permite a formação de uma rede para análises posteriores

---

Desenvolvido por [Matheus Ferreira](mailto:mff.matheusfernandes@gmail.com)
