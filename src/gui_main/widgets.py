def select_sample(self, index):
    """ """
    if index:
        selection = index[-1]
        self.current_sample = current_sample(self.data_bulk, selection)
        self.update_plots()


def next_sample(self):
    current = self.sample_list.curselection()
    if not current:  # See if selection exists
        return
    current = current[-1]  # Grab actucal number
    total = self.sample_list.size()
    new = current + 1
    if current < (total - 1):
        self.sample_list.select_clear(current)
        self.sample_list.selection_set(new)
        self.sample_list.see(new)
        self.select_sample(self.sample_list.curselection())


def previous_sample(self):
    current = self.sample_list.curselection()[-1]
    if not current:
        return
    new = current - 1
    if current > 0:
        self.sample_list.select_clear(current)
        self.sample_list.selection_set(new)
        self.sample_list.see(new)
        self.select_sample(self.sample_list.curselection())
