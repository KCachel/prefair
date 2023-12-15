library(tidyverse)
library(ggnuplot)
library(ggpubr)
library(ggthemes)

econ_equal <- read_csv("econ-freedom/results_equal_rep.csv")
gsci_equal <- read_csv("global-sci/results_equal_rep.csv")
ibmhr_equal <- read_csv("ibmhr/results_equal_rep.csv")
wh_equal <- read_csv("world-happiness/results_equal_rep.csv")
econ_prop <- read_csv("econ-freedom/results_prop_rep.csv")
gsci_prop <- read_csv("global-sci/results_prop_rep.csv")
ibmhr_prop <- read_csv("ibmhr/results_prop_rep.csv")
wh_prop <- read_csv("world-happiness/results_prop_rep.csv")

syn <- read_csv("synthetic-study/synthetic.csv")%>%
  mutate(method=recode(method,
                       `BALANCED-COMMITTEE-ELECTION` = "FMWV")) %>% 
  dplyr::rename(Method = method) %>%
  mutate(`Distinct Groups` = str_count(consensusranking_grp_cnts, ',')+1)

syn$pNDKL <- signif(syn$pNDKL, digits = 3)
syn$SFD <- signif(syn$SFD, digits = 3)
syn$NDKL <- signif(syn$NDKL, digits = 3)
syn$`kl_div_pool_profile` <- signif(syn$`kl_div_pool_profile`, digits = 3)


yy_string <- "Agreement (\U03B1)"
xx_string <- "Preference Completeness"
fill_limits <- c(0,1.4)
textsize <- 3


red_high <- "#BE1316"
blue_high <- "#05b4dd"



dataset <- ggplot(syn, aes(profile_percentage, dispersion)) +
  geom_tile(aes(fill = syn$`kl_div_pool_profile`)) +
  #geom_tile(aes(fill = pNDKL, colour = "black", size=0.15)) +
  scale_fill_gradient(low = "#D7D7D7", high = "#BE1316", limits = fill_limits)+
  #scale_fill_distiller(palette = "RdYlBu", limits = fill_limits)+
  geom_text(aes(label = syn$`kl_div_pool_profile`), size = textsize+1, color = "black")+
  labs(title =  'KL-divergence Between Profile and Pool')+
  theme_gnuplot()+
  theme(legend.position = "right",
        legend.direction = "vertical",
    plot.background=element_blank(),
    panel.border=element_blank(),
    axis.text.x = element_text(margin = margin(t = 3)),
    axis.text.y = element_text(margin = margin(r = 3)),
    axis.ticks = element_blank())+
  scale_x_continuous(name = xx_string, breaks=c(.2,.4,.6,.8,1), expand=c(0,0))+
  scale_y_continuous(name = yy_string, breaks=c(0,.2,.4,.6,.8,1), expand=c(0,0))+
  labs(fill='KL-div.')


ggsave(dataset, filename = glue::glue("plots/dataset_data.pdf"), device = cairo_pdf,
       width = 5, height = 2.5, units = "in")



make_heatmap <-function(Method, col) {
  
  data <-  syn %>%
    filter(.data$Method == .env$Method)
  
  
  p <- ggplot(data, aes(profile_percentage, dispersion)) +
    geom_tile(aes(fill = data[[col]])) +
    #geom_tile(aes(fill = pNDKL, colour = "black", size=0.15)) +
    #scale_fill_gradient(low = "#D7D7D7", high = "#f4aa4a", limits = fill_limits)+
    scale_fill_distiller(palette = "RdYlBu", limits = fill_limits)+
    geom_text(aes(label = data[[col]]), size = textsize, color = "black")+
    labs(title =  glue::glue({Method}))+
    theme_gnuplot()+
    theme(
    # theme(legend.position = "right",
    #       legend.direction = "vertical",
          legend.position = "none",
          plot.background=element_blank(),
          panel.border=element_blank(),
          axis.text.x = element_text(margin = margin(t = 3)),
          axis.text.y = element_text(margin = margin(r = 3)),
          axis.ticks = element_blank())+
    scale_x_continuous(name = xx_string, breaks=c(.2,.4,.6,.8,1), expand=c(0,0))+
    scale_y_continuous(name = yy_string, breaks=c(0,.2,.4,.6,.8,1), expand=c(0,0))
  
  return(p)
}

legend_heatmap <-function(col) {
  
  legend <- ggplot(syn, aes(profile_percentage, dispersion)) +
    geom_tile(aes(fill = syn[[col]]), colour = "black") +
    #scale_fill_gradient(low = "#D7D7D7", high = "#f4aa4a", limits = fill_limits)+
    scale_fill_distiller(palette = "RdYlBu", limits = fill_limits)+
    lims(x = c(0,0), y = c(0,0))+
    theme_void()+
    theme(legend.position = c(0.5,0.5),
          #legend.key.size = unit(1, "cm"),
          legend.text = element_text(size =  12),
          legend.title = element_text(size = 15))+
    labs(fill=col)

  return(legend)
}


#pNDKL

borda<-make_heatmap('BORDA', 'pNDKL')
prefair<-make_heatmap('PREFAIR', 'pNDKL')
epira <-make_heatmap('EPIRA', 'pNDKL')
fmwv <-make_heatmap('FMWV', 'pNDKL')
mc4 <-make_heatmap('MC4', 'pNDKL')
rapf <-make_heatmap('RAPF', 'pNDKL')
stv <-make_heatmap('STV', 'pNDKL')
legend <-legend_heatmap('pNDKL')


fig_maps<- ggarrange(prefair, fmwv, epira, legend, borda, mc4, rapf, stv, 
                        ncol = 4, nrow = 2)
pdfwidth <- 12
pdfheight <- 4

ggsave(fig_maps, filename = glue::glue("plots/maps.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")




#SFD

borda<-make_heatmap('BORDA', 'SFD')
prefair<-make_heatmap('PREFAIR', 'SFD')
epira <-make_heatmap('EPIRA', 'SFD')
fmwv <-make_heatmap('FMWV', 'SFD')
mc4 <-make_heatmap('MC4', 'SFD')
rapf <-make_heatmap('RAPF', 'SFD')
stv <-make_heatmap('STV', 'SFD')
legend <-legend_heatmap('SFD')


fig_maps<- ggarrange(prefair, fmwv, epira, legend, borda, mc4, rapf, stv, 
                     ncol = 4, nrow = 2)
pdfwidth <- 12
pdfheight <- 4

ggsave(fig_maps, filename = glue::glue("plots/SFD_maps.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")


#NDKL

borda<-make_heatmap('BORDA', 'NDKL')
prefair<-make_heatmap('PREFAIR', 'NDKL')
epira <-make_heatmap('EPIRA', 'NDKL')
fmwv <-make_heatmap('FMWV', 'NDKL')
mc4 <-make_heatmap('MC4', 'NDKL')
rapf <-make_heatmap('RAPF', 'NDKL')
stv <-make_heatmap('STV', 'NDKL')
legend <-legend_heatmap('NDKL')


fig_maps<- ggarrange(prefair, fmwv, epira, legend, borda, mc4, rapf, stv, 
                     ncol = 4, nrow = 2)
pdfwidth <- 12
pdfheight <- 4

ggsave(fig_maps, filename = glue::glue("plots/NDKL_maps.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")


#counts - how many groups are in each consensus
make_heatmap_dg <-function(Method, col) {
  
  data <-  syn %>%
    filter(.data$Method == .env$Method)
  
  
  p <- ggplot(data, aes(profile_percentage, dispersion)) +
    geom_tile(aes(fill = data[[col]])) +
    #geom_tile(aes(fill = pNDKL, colour = "black", size=0.15)) +
    #scale_fill_gradient(low = "#D7D7D7", high = "#f4aa4a", limits = fill_limits)+
    scale_fill_distiller(palette = "RdYlBu", limits = c(1,4), direction=1)+
    geom_text(aes(label = data[[col]]), size = textsize, color = "black")+
    labs(title =  glue::glue({Method}))+
    theme_gnuplot()+
    theme(
      # theme(legend.position = "right",
      #       legend.direction = "vertical",
      legend.position = "none",
      plot.background=element_blank(),
      panel.border=element_blank(),
      axis.text.x = element_text(margin = margin(t = 3)),
      axis.text.y = element_text(margin = margin(r = 3)),
      axis.ticks = element_blank())+
    scale_x_continuous(name = xx_string, breaks=c(.2,.4,.6,.8,1), expand=c(0,0))+
    scale_y_continuous(name = yy_string, breaks=c(0,.2,.4,.6,.8,1), expand=c(0,0))
  
  return(p)
}

legend_heatmap_dg <-function(col) {
  
  legend <- ggplot(syn, aes(profile_percentage, dispersion)) +
    geom_tile(aes(fill = syn[[col]]), colour = "black") +
    #scale_fill_gradient(low = "#D7D7D7", high = "#f4aa4a", limits = fill_limits)+
    scale_fill_distiller(palette = "RdYlBu", limits = c(1,4), direction=1)+
    lims(x = c(0,0), y = c(0,0))+
    theme_void()+
    theme(legend.position = c(0.5,0.5),
          #legend.key.size = unit(1, "cm"),
          legend.text = element_text(size =  12),
          legend.title = element_text(size = 15))+
    labs(fill=col)
  
  return(legend)
}

borda<-make_heatmap_dg('BORDA', 'Distinct Groups')
prefair<-make_heatmap_dg('PREFAIR', 'Distinct Groups')
epira <-make_heatmap_dg('EPIRA', 'Distinct Groups')
fmwv <-make_heatmap_dg('FMWV', 'Distinct Groups')
mc4 <-make_heatmap_dg('MC4', 'Distinct Groups')
rapf <-make_heatmap_dg('RAPF', 'Distinct Groups')
stv <-make_heatmap_dg('STV', 'Distinct Groups')
legend <-legend_heatmap_dg('Distinct Groups')


fig_maps<- ggarrange(prefair, fmwv, epira, legend, borda, mc4, rapf, stv, 
                     ncol = 4, nrow = 2)
pdfwidth <- 12
pdfheight <- 4

ggsave(fig_maps, filename = glue::glue("plots/DistinctGroups_maps.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")





equal_df <- Reduce(function(x, y) merge(x, y, all=TRUE), list(econ_equal,
                                                              gsci_equal, ibmhr_equal, wh_equal))%>%
  mutate(Rep = 'equal')

prop_df <- Reduce(function(x, y) merge(x, y, all=TRUE), list(econ_prop,
                                                             gsci_prop, ibmhr_prop, wh_prop))%>%
  mutate(Rep = 'prop')

datasets <- Reduce(function(x, y) merge(x, y, all=TRUE), list(equal_df, prop_df))%>%
  mutate(method=recode(method,
                             `BALANCED-COMMITTEE-ELECTION` = "FMWV")) %>% 
  dplyr::rename(Method = method)

datasets <- datasets %>%
  subset(Method !=c('PREFAIR(IMPUTE) + EPIRA')) %>%
  subset(Method !=c( 'PREFAIR(IMPUTE) + RAPF'))



pt_size <- 3.5 #3
title_size <- 10
linesize <- 1
axistext <- 14
x_string <- "NDKL"
y_string <- "SFD"
x_stringsat <- "Depth"
y_stringsat <- "Average Sat"



#multi_colors <- c('darkviolet', '#009e73', '#56b4e9','#e69f00', '#f0e442', 'red', 'black')

multi_colors<- c( '#ff7f0e','#1f77b4', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2')


multi_shapes <- c(16, 15, 18, 8, 17, 20, 7)


data <- datasets %>%
  filter(dataset == 'IBMHR') %>%
  filter(Rep == 'equal') %>%
  pivot_longer(starts_with("avg"), names_to = "Depth", values_to = "AvgSat") %>%
  mutate(Depth=recode(Depth,
                       `avg_sat_10` = .1,
                       `avg_sat_20` = .2,
                       `avg_sat_30` = .3,
                       `avg_sat_40` = .4,
                       `avg_sat_50` = .5))
  










make_sat_plot <-function(dataset, rep) {
  
  data <-  datasets %>%
    filter(.data$Rep == .env$rep) %>%
    filter(.data$dataset == .env$dataset) %>%
    pivot_longer(starts_with("avg"), names_to = "Depth", values_to = "AvgSat") %>%
    mutate(Depth=recode(Depth,
                        `avg_sat_10` = .1,
                        `avg_sat_20` = .2,
                        `avg_sat_30` = .3,
                        `avg_sat_40` = .4,
                        `avg_sat_50` = .5))
  
  data$Method <- factor(data$Method, levels = c("PREFAIR","BORDA","EPIRA","FMWV", "MC4", "RAPF", "STV")) 
  
  
  p <- ggplot(data, aes(color = Method, x  = Depth, y = AvgSat, shape = Method)) +
    geom_point(size = pt_size)+
    geom_line(size = linesize)+
    #theme_gnuplot()+
    xlab(x_stringsat)+
    ylab(y_stringsat)+
    ylim(0,1)+
    theme_gnuplot()+
    theme(legend.position = "top",
          legend.direction = "horizontal",
          axis.title.y = element_text(size = axistext, margin = margin(r = 1)),
          axis.title.x = element_text(size = axistext,margin = margin(t = 1)),
          axis.text.x = element_text(margin = margin(t = 3)),
          axis.text.y = element_text(margin = margin(r = 3)))+
    ggtitle(glue::glue("{dataset}"))+
    scale_shape_manual(values=multi_shapes)+
    scale_color_manual(values=multi_colors)+
    guides(color=guide_legend(nrow=1))+
    guides(shape = guide_legend(nrow = 1))
  
  return(p)
}

sat_eq_econf <- make_sat_plot('Econ Freedom', 'equal')
sat_eq_ibm <- make_sat_plot('IBMHR', 'equal')
sat_eq_wh <- make_sat_plot('World Happiness', 'equal')
sat_eq_gsci <- make_sat_plot('GSCI', 'equal')



pdfwidth <- 14
pdfheight <- 3.2

pdfwidth <- 10
pdfheight <- 2.5


fig_sat_eq <- ggarrange(sat_eq_econf, sat_eq_ibm,sat_eq_wh, sat_eq_gsci,
                         ncol = 4, nrow = 1, common.legend = TRUE, legend = "top")

ggsave(fig_sat_eq, filename = glue::glue("plots/datasets_sat_equal.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")

sat_p_econf <- make_sat_plot('Econ Freedom', 'prop')
sat_p_ibm <- make_sat_plot('IBMHR', 'prop')
sat_p_wh <- make_sat_plot('World Happiness', 'prop')
sat_p_gsci <- make_sat_plot('GSCI', 'prop')

fig_sat_prop <- ggarrange(sat_p_econf, sat_p_ibm, sat_p_wh, sat_p_gsci,
                           ncol = 4, nrow = 1, common.legend = TRUE, legend = "top")

ggsave(fig_sat_prop, filename = glue::glue("plots/datasets_sat_prop.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")




make_fairness_plot <-function(dataset, rep) {
  
  data <-  datasets %>%
    filter(.data$Rep == .env$rep) %>%
    filter(.data$dataset == .env$dataset)
  data$Method <- factor(data$Method, levels = c("PREFAIR","BORDA","EPIRA","FMWV", "MC4", "RAPF", "STV")) 
  
  
  p <- ggplot(data, aes(color = Method, x  = NDKL, y = SFD, shape = Method)) +
    geom_point(size = pt_size)+
    #geom_line(size = linesize)+
    #theme_gnuplot()+
    xlab(x_string)+
    ylab(y_string)+
    theme_gnuplot()+
    theme(legend.position = "top",
          legend.direction = "horizontal",
          axis.title.y = element_text(size = axistext, margin = margin(r = 1)),
          axis.title.x = element_text(size = axistext,margin = margin(t = 1)),
          axis.text.x = element_text(margin = margin(t = 3)),
          axis.text.y = element_text(margin = margin(r = 3)))+
    ggtitle(glue::glue("{dataset}"))+
    scale_shape_manual(values=multi_shapes)+
    scale_color_manual(values=multi_colors)+
    guides(color=guide_legend(nrow=1))+
    guides(shape = guide_legend(nrow = 1))
  
  return(p)
}
pdfwidth <- 14
pdfheight <- 3.2

pdfwidth <- 10
pdfheight <- 2.5


eq_econf <- make_fairness_plot('Econ Freedom', 'equal')
eq_ibm <- make_fairness_plot('IBMHR', 'equal')
eq_wh <- make_fairness_plot('World Happiness', 'equal')
eq_gsci <- make_fairness_plot('GSCI', 'equal')

fig_fair_eq <- ggarrange(eq_econf, eq_ibm,eq_wh, eq_gsci,
                   ncol = 4, nrow = 1, common.legend = TRUE, legend = "top")

ggsave(fig_fair_eq, filename = glue::glue("plots/datasets_fair_equal.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")

p_econf <- make_fairness_plot('Econ Freedom', 'prop')
p_ibm <- make_fairness_plot('IBMHR', 'prop')
p_wh <- make_fairness_plot('World Happiness', 'prop')
p_gsci <- make_fairness_plot('GSCI', 'prop')

fig_fair_prop <- ggarrange(p_econf, p_ibm, p_wh, p_gsci,
                         ncol = 4, nrow = 1, common.legend = TRUE, legend = "top")

ggsave(fig_fair_prop, filename = glue::glue("plots/datasets_fair_prop.pdf"), device = cairo_pdf,
       width = pdfwidth, height = pdfheight, units = "in")

