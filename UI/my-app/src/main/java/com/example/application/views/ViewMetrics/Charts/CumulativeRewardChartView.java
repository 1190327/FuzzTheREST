package com.example.application.views.ViewMetrics.Charts;

import com.google.gson.Gson;
import com.vaadin.flow.component.dependency.JsModule;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;

import java.util.List;

@JsModule("./charts/plotly-vaadin.js")
public class CumulativeRewardChartView extends VerticalLayout {

    public CumulativeRewardChartView(List<Double> cumulativeRewards) {
        Div chartContainer = new Div();
        chartContainer.setId("cumulativeRewardChart");
        add(chartContainer);
        setSizeFull();

        CumulativeRewardData data = new CumulativeRewardData(cumulativeRewards);

        Gson gson = new Gson();
        String dataJson = gson.toJson(data);

        chartContainer.getElement().executeJs("window.renderCumulativeRewardChart($0, $1)", chartContainer.getId().get(), dataJson);
    }

    private static class CumulativeRewardData {
        private List<Double> cumulativeRewards;

        public CumulativeRewardData(List<Double> cumulativeRewards) {
            this.cumulativeRewards = cumulativeRewards;
        }
    }
}
