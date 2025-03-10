import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'cleanPath'
})
export class CleanPathPipe implements PipeTransform {

  transform(value: string, args?: any): string { 
    if (value) {
      return value
            .replace(/^[0-9]+/g, '')
            .replace(/_/g, ' ')
            .replace(/\.[^/.]+$/, '');
    } 
  }

}
