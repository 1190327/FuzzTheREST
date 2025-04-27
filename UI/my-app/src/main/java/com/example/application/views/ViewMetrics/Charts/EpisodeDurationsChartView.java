package com.example.application.views.ViewMetrics.Charts;

import com.google.gson.Gson;
import com.vaadin.flow.component.dependency.JsModule;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;

import java.util.List;

@JsModule("./charts/plotly-vaadin.js")
public class EpisodeDurationsChartView extends VerticalLayout {

    public EpisodeDurationsChartView(List<Double> episodeDurations) {
        Div chartContainer = new Div();
        chartContainer.setId("episodeDurationsChart");
        add(chartContainer);
        setSizeFull();

        EpisodeDurationsData episodeDurationsData = new EpisodeDurationsData();
        episodeDurationsData.setEpisodeDurations(episodeDurations);

        Gson gson = new Gson();
        String dataJson = gson.toJson(episodeDurationsData);

        chartContainer.getElement().executeJs("window.renderEpisodeDurationsChart($0, $1)", chartContainer.getId().get(), dataJson);
    }

    private static class EpisodeDurationsData {
        private List<Double> episodeDurations;

        public List<Double> getEpisodeDurations() {
            return episodeDurations;
        }

        public void setEpisodeDurations(List<Double> episodeDurations) {
            this.episodeDurations = episodeDurations;
        }
    }
}
