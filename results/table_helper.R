econ_equal <- read_csv("econ-freedom/results_equal_rep.csv")
gsci_equal <- read_csv("global-sci/results_equal_rep.csv")
ibmhr_equal <- read_csv("ibmhr/results_equal_rep.csv")
wh_equal <- read_csv("world-happiness/results_equal_rep.csv")
econ_prop <- read_csv("econ-freedom/results_prop_rep.csv")
gsci_prop <- read_csv("global-sci/results_prop_rep.csv")
ibmhr_prop <- read_csv("ibmhr/results_prop_rep.csv")
wh_prop <- read_csv("world-happiness/results_prop_rep.csv")


equal_df <- Reduce(function(x, y) merge(x, y, all=TRUE), list(econ_equal,
                                                              gsci_equal, ibmhr_equal, wh_equal))%>%
  mutate(Rep = 'equal')

prop_df <- Reduce(function(x, y) merge(x, y, all=TRUE), list(econ_prop,
                                                             gsci_prop, ibmhr_prop, wh_prop))%>%
  mutate(Rep = 'prop')

dataset <- Reduce(function(x, y) merge(x, y, all=TRUE), list(equal_df, prop_df))%>%
  subset(method !=c('BORDA')) %>%
  subset(method !=c('EPIRA')) %>%
  subset(method !=c('BALANCED-COMMITTEE-ELECTION')) %>%
  subset(method !=c('MC4')) %>%
  subset(method !=c('RAPF')) %>%
  subset(method !=c('STV')) %>%
  select(method, dataset, SFD, pNDKL, NDKL, avg_sat_10, avg_sat_20, avg_sat_30, avg_sat_40, avg_sat_50, Rep)
  

write_csv(dataset, "table_data.csv")