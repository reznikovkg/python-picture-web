const TABLE_DATA_KEY = 'tableData'

const state = {
    tableData: JSON.parse(localStorage.getItem(TABLE_DATA_KEY)) || [],
};

const mutations = {
    ADD_TABLE_DATA(state, newData) {
        state.tableData.push(newData);
        localStorage.setItem(TABLE_DATA_KEY, JSON.stringify(state.tableData));
    },
    REMOVE_TABLE_DATA(state, index) {
        state.tableData.splice(index, 1);
        localStorage.setItem(TABLE_DATA_KEY, JSON.stringify(state.tableData));
    },
};

const actions = {
    addTableData({ commit }, newData) {
        commit('ADD_TABLE_DATA', newData);
    },
    removeTableData({ commit }, index) {
        commit('REMOVE_TABLE_DATA', index);
    },
};

const getters = {
    getTableData: (state) => state.tableData,
};

export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters,
};
