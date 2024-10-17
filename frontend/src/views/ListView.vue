<template>
  <div class="list">
    <h1>Результат</h1>
    <TableComponent :data="tableStub"/>
  </div>
</template>

<script>
import TableComponent from '@/components/TableComponent.vue';

export default {
  name: 'ListVue',
  components: {
    TableComponent,
  },
  data() {
    return {
      tableStub: [
        {
          image: 'image1.jpg',
          firstModelResult: 'A',
          secondModelResult: 'B',
          thirdModelResult: 'C',
          ensembleModelsResult: 'D'
        },
        {
          image: 'image2.jpg',
          firstModelResult: 'E',
          secondModelResult: 'F',
          thirdModelResult: 'G',
          ensembleModelsResult: 'H'
        },
        {
          image: 'image3.jpg',
          firstModelResult: 'I',
          secondModelResult: 'J',
          thirdModelResult: 'K',
          ensembleModelsResult: 'L'
        },
        {
          image: 'image4.jpg',
          firstModelResult: 'M',
          secondModelResult: 'N',
          thirdModelResult: 'O',
          ensembleModelsResult: 'P'
        },
        {
          image: 'image5.jpg',
          firstModelResult: 'Q',
          secondModelResult: 'R',
          thirdModelResult: 'S',
          ensembleModelsResult: 'T'
        },
        {
          image: 'image6.jpg',
          firstModelResult: 'U',
          secondModelResult: 'V',
          thirdModelResult: 'W',
          ensembleModelsResult: 'X'
        },
      ],
    };
  },
};
</script>
